import os
from fastapi import FastAPI, Depends,Request, HTTPException ,UploadFile, File ,Body,Form
from sqlalchemy.orm import Session
from app import connexion_db
from typing import Optional,Union
from app.auth import authentication, models, schemas
from app.auth.schemas import UserLogin, Token
from fastapi import HTTPException
from app.auth.models import PdfDocument, User
from pydantic import BaseModel
from app.auth.dependencies import get_current_user , get_current_user_optional
from app.rag.create_embedding import create_user_embeddings
from app.rag.get_document_reterived import retrieve_user_documents
from app.chat.service import chat_with_agent, get_conversation_with_messages, get_messages_paginated , get_or_create_conversation, get_user_conversations , save_message
from app.auth import authentication
import requests
from jose import jwt
from app.agent.storage_utils import ocr_image
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.middleware import guest_user_middleware
from app.agent.context import Context
from app.auth.schemas import ChatRequest, ChatResponse
from app.chat import service
import uuid
from fastapi.responses import FileResponse
from pdf2image import convert_from_bytes
import io
from prometheus_fastapi_instrumentator import Instrumentator

# Crée la DB si pas déjà
models.Base.metadata.create_all(bind=connexion_db.engine)

app = FastAPI()
app.middleware("http")(guest_user_middleware)
Instrumentator().instrument(app).expose(app)
origins = [
    "http://localhost:3000",  # frontend Next.js
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],        # autorise GET, POST, OPTIONS...
    allow_headers=["*"],        # autorise tous les headers
)
# Dependency
get_db = connexion_db.get_db



class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[int] = None
    user_id: Optional[Union[int, str]] = None

@app.post("/test-chat")
async def chat(
    request: Request,
    db: Session = Depends(get_db),
    query: str = Form(...),
    conversation_id: Optional[int] = Form(None),
    file: UploadFile | None = File(None),
    user_id: Optional[Union[int, str]]= Form(None)
):
    # 🔹 reconstruire le payload
    payload = QueryRequest(
        query=query,
        conversation_id=conversation_id,
        user_id=user_id  
    )
    
    query_text = payload.query.strip() if payload.query else None

    if not query_text and not file:
        raise HTTPException(
            status_code=400,
            detail="Veuillez fournir une question, une image ou un PDF."
        )
    print(f"the user id from front-end is : ${payload.user_id}")
    
    user_id = payload.user_id if payload.user_id is not None else request.state.user_id
    print(f"[CHAT] user_id = {user_id}")

    is_guest = isinstance(user_id, str) and user_id.startswith("guest-")
    conversation = None

   
    if not is_guest:
        conversation = get_or_create_conversation(
            db=db,
            user_id=user_id,
            conversation_id=payload.conversation_id,
            first_message=query_text or "File input"
        )

        if query_text:
            save_message(
                db=db,
                conversation_id=conversation.id,
                role="user",
                content=query_text
            )

    # =========================
    # 🔹 4. Gestion du fichier
    # =========================
    image_text = None
    pdf_name = None

    if file:
        filename = file.filename.lower()
        file_bytes = await file.read()

        # 🔸 PDF
        if filename.endswith(".pdf") and not is_guest:
            user_pdf_dir = f"storage/users/user_{user_id}/pdfs"
            os.makedirs(user_pdf_dir, exist_ok=True)

            file_path = os.path.join(user_pdf_dir, file.filename)
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            pdf = PdfDocument(
                filename=file.filename,
                filepath=file_path,
                user_id=user_id
            )
            db.add(pdf)
            db.commit()

            create_user_embeddings(user_id)
            
            pdf_name = file.filename

        # 🔸 Image
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            user_img_dir = f"storage/users/user_{user_id}/images"
            os.makedirs(user_img_dir, exist_ok=True)

            image_path = os.path.join(user_img_dir, file.filename)
            with open(image_path, "wb") as f:
                f.write(file_bytes)

            image_text = ocr_image(image_path) 
            print(f"the text of image {image_text}")

    # =========================
    # 🔹 5. Appel du chatbot (TOUJOURS)
    # =========================
    answer = chat_with_agent(
        user_id=user_id,
        query=query_text,
        image_text=image_text,
        pdf_name=pdf_name
    )

    # 🔹 6. Sauvegarde réponse assistant
    if not is_guest and conversation:
        save_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content=answer
        )

    return {
        "answer": answer,
        "conversation_id": conversation.id if conversation else None,
        "user_id": user_id
    }


@app.get("/conversations")
def get_conversations(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.state.user_id

    conversations = get_user_conversations(db, user_id)

    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at
        }
        for c in conversations
    ]

@app.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.state.user_id

    conversation = get_conversation_with_messages(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at
            }
            for m in conversation.messages
        ]
    }

@app.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    request: Request,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    user_id = request.state.user_id
    
    messages = get_messages_paginated(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
        limit=limit,
        offset=offset
    )

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at
        }
        for m in messages
    ]


# Endpoint test
@app.get("/")
def read_root():
    return {"message": "hello issam your API is work good!"}

# Endpoint pour créer un utilisateur
@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Vérifier si email existe déjà
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        
        # Hasher le mot de passe
        hashed_password = authentication.hash_password(user.mot_de_passe)
        
        db_user = models.User(
            nom=user.nom,
            prenom=user.prenom,
            adress=user.adress,
            email=user.email,
            mot_de_passe=hashed_password,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except Exception as e:
        # Affiche l'erreur exacte dans le terminal et renvoie dans la réponse
        print("Erreur lors de l'ajout de l'utilisateur:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/me")
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return {
        "first_name": current_user.nom,
        "last_name": current_user.prenom,
        "adress": current_user.adress,
        "email": current_user.email,
        "role": current_user.role
    }

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        # Cherche l'utilisateur par email
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")
        
        # Vérifie le mot de passe
        if not authentication.verify_password(user.mot_de_passe, db_user.mot_de_passe):
            raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")
        
        # Création du token
        token = authentication.create_access_token({"sub": str(db_user.id)})
        return {"access_token": token, "token_type": "bearer"}
    
    except HTTPException as e:
        # Remonte les HTTPException (400 par ex.)
        raise e
    except Exception as e:
        # Capture toutes les autres erreurs
        print("Erreur lors de la connexion :", e)
        raise HTTPException(status_code=500, detail="Erreur interne lors de la connexion")




load_dotenv(dotenv_path=".env")  # 👈 IMPORTANT

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_REDIRECT_URI_SIGNUP = os.getenv("GOOGLE_REDIRECT_URI_SIGNUP")

@app.post("/login/google", response_model=Token)
def login_google(code: str = Form(...), db: Session = Depends(get_db)):
    """
    Recevoir le code d'autorisation Google, récupérer l'utilisateur et générer un JWT local.
    """
    try:
        # 1️⃣ Échanger le code contre access_token et id_token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        

        token_response = requests.post(token_url, data=data)
        token_response.raise_for_status()
        token_data = token_response.json()
        google_id_token = token_data["id_token"]

        # 2️⃣ Vérifier le token JWT Google et extraire les infos
        
        google_payload = id_token.verify_oauth2_token(
            google_id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
)

        email = google_payload["email"]
        print(f"your email is {email}")
        nom = google_payload.get("given_name", "")
        print(f"your last name is {nom}")
        prenom = google_payload.get("family_name", "")
        print(f"your first name is {prenom}")
        
        # 3️⃣ Chercher ou créer l'utilisateur dans la DB
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            # Création d'un utilisateur Google
            user = models.User(
                email=email,
                nom=nom,
                prenom=prenom,
                mot_de_passe="",  # vide car pas de mot de passe local
                role="user"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 4️⃣ Créer ton JWT local
        access_token = authentication.create_access_token({"sub": str(user.id)})
        #token = auth.create_access_token({"sub": str(db_user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print("Erreur login Google:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion Google")


@app.post("/signup/google", response_model=schemas.UserGoogleOut)
def signup_google(code: str = Form(...), db: Session = Depends(get_db)):
    """
    Recevoir le code d'autorisation Google, récupérer l'utilisateur.
    Retourner uniquement email, nom et prenom, sans sauvegarder dans la DB.
    """
    try:
        # 1️⃣ Échanger le code contre access_token et id_token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI_SIGNUP,
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_url, data=data)
        token_response.raise_for_status()
        token_data = token_response.json()
        google_id_token = token_data["id_token"]

        # 2️⃣ Vérifier le token Google
        google_payload = id_token.verify_oauth2_token(
            google_id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = google_payload["email"]
        nom = google_payload.get("given_name", "")
        prenom = google_payload.get("family_name", "")

        # 3️⃣ Retourner uniquement les infos
        return {
            "email": email,
            "nom": nom,
            "prenom": prenom,
            "role": "user"
        }

    except Exception as e:
        print("Erreur signup Google:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de l'inscription Google")
    

@app.post("/user-non-connected", response_model=schemas.ChatResponse)
def chat(
    payload: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(get_current_user_optional)
):
    # 🔐 USER CONNECTÉ
    if current_user:
        identity = f"user:{current_user.id}"

    # 👤 GUEST
    elif payload.guest_id:
        identity = f"guest:{payload.guest_id}"

    else:
        raise HTTPException(status_code=400, detail="No identity provided")

    # 👉 Ici tu appelles TON agent / LLM
    # Pour l’instant mock propre
    reply = f"🤖 (identity={identity}) J'ai bien reçu : {payload.message}"

    return { "reply": reply }

@app.post("/upload-pdf")
def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),  # ✅ ici
    db: Session = Depends(get_db)
):
    user_dir = f"storage/users/user_{current_user.id}/pdfs"
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    pdf = PdfDocument(
        filename=file.filename,
        filepath=file_path,
        user_id=current_user.id
    )
    db.add(pdf)
    db.commit()
    create_user_embeddings(current_user.id)
    return {"message": "PDF uploadé avec succès"}

@app.post("/query")
def query_documents(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint pour que l'utilisateur récupère les documents pertinents
    Payload attendu: {"query": "ma question ici"}
    """
    query_text = payload.query

    if not query_text:
        raise HTTPException(status_code=400, detail="Query manquante")

    # Récupération des documents pertinents
    docs = retrieve_user_documents(current_user.id, query_text)

    if not docs:
        return {"message": "Aucun document pertinent trouvé", "results": []}

    # Formater la réponse
    results = []
    for doc, score in docs:
        results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "similarity_score": score
        })

    return {"results": results}

@app.post("/chat")
def chat(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    query_text = payload.query.strip()

    if not query_text:
        raise HTTPException(status_code=400, detail="Query manquante")
   

    # Générer et stocker automatiquement les préférences de l'utilisateur
    #initialize_user_preferences(current_user.id, db_session)

    answer = chat_with_agent(
        user_id=current_user.id,
        query=query_text
    )

    return {"answer": answer}
@app.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    query: str = "",
    current_user: User = Depends(get_current_user)
):
    file_bytes = await file.read()

    user_dir = os.path.join("storage", "users", f"user_{current_user.id}", "images")
    os.makedirs(user_dir, exist_ok=True)

    image_path = os.path.join(user_dir, file.filename)
    with open(image_path, "wb") as f:
        f.write(file_bytes)

    image_text = ocr_image(image_path)

    response = chat_with_agent(
        user_id=current_user.id,
        query=query,
        image_text=image_text
    )

    return {
        "response": response,
        "image_text": image_text
    }


from pathlib import Path

# Dossier pour stocker les images générées depuis PDF
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/pdf/preview")
async def pdf_preview(file: UploadFile = File(...)):
    # Lire le PDF
    pdf_bytes = await file.read()
    pages = convert_from_bytes(pdf_bytes, dpi=150)
    first_page = pages[0]

    # Sauvegarder la première page en PNG
    filename = f"{UPLOAD_DIR}/{file.filename.replace('.pdf','')}_page1.png"
    first_page.save(filename, format="PNG")

    # Retourner l'URL de l'image
    print("le ")
    return {"url": f"http://127.0.0.1:8000/{filename}"}

# Endpoint pour servir les fichiers statiques du dossier uploads
@app.get("/uploads/{file_name}")
async def serve_file(file_name: str):
    file_path = UPLOAD_DIR / file_name
    if file_path.exists():
        return FileResponse(file_path)
    return {"error": "File not found"}