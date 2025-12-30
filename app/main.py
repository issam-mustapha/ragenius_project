import os
from fastapi import FastAPI, Depends, HTTPException ,UploadFile, File ,Body,Form
from sqlalchemy.orm import Session
from app import connexion_db
from auth import auth, models, schemas
from auth.schemas import UserLogin, Token
from fastapi import HTTPException
from auth.models import PdfDocument, User
from pydantic import BaseModel
from auth.dependencies import get_current_user
from app.rag.create_embedding import create_user_embeddings
from app.rag.get_document_reterived import retrieve_user_documents
from app.chat.chatbot import chat_with_agent
from auth import auth
import requests
from jose import jwt


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI") 

# Crée la DB si pas déjà
models.Base.metadata.create_all(bind=connexion_db.engine)

app = FastAPI()

# Dependency
get_db = connexion_db.get_db

#to recieve query payload
class QueryRequest(BaseModel):
    query: str
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
        hashed_password = auth.hash_password(user.mot_de_passe)
        
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


@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        # Cherche l'utilisateur par email
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")
        
        # Vérifie le mot de passe
        if not auth.verify_password(user.mot_de_passe, db_user.mot_de_passe):
            raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")
        
        # Création du token
        token = auth.create_access_token({"sub": db_user.email})
        return {"access_token": token, "token_type": "bearer"}
    
    except HTTPException as e:
        # Remonte les HTTPException (400 par ex.)
        raise e
    except Exception as e:
        # Capture toutes les autres erreurs
        print("Erreur lors de la connexion :", e)
        raise HTTPException(status_code=500, detail="Erreur interne lors de la connexion")

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
        id_token = token_data["id_token"]

        # 2️⃣ Vérifier le token JWT Google et extraire les infos
        
        google_payload = jwt.decode(id_token, options={"verify_signature": True})
        email = google_payload["email"]
        nom = google_payload.get("given_name", "")
        prenom = google_payload.get("family_name", "")

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
        access_token = auth.create_access_token({"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        print("Erreur login Google:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion Google")


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
