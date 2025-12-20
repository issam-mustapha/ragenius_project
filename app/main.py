from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import connexion_db
from auth import auth, models, schemas
from auth.schemas import UserLogin, Token
from fastapi import HTTPException
# Crée la DB si pas déjà
models.Base.metadata.create_all(bind=connexion_db.engine)

app = FastAPI()

# Dependency
get_db = connexion_db.get_db

# Endpoint test
@app.get("/")
def read_root():
    return {"message": "API fonctionne!"}

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

