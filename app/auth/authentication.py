# auth.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from fastapi import Depends, HTTPException

from sqlalchemy.orm import Session
from app.connexion_db import get_db

# ==============================
# Configuration JWT
# ==============================
SECRET_KEY = "ksdjffdsjoewr98095fjkfdsjekfdsjfsajofdsj_kfdsjpfsakofnvknckjfdsoijds"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24  # 1 jour

# ==============================
# Context de hashage avec Argon2
# ==============================
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# ==============================
# Fonctions mot de passe
# ==============================
def hash_password(password: str) -> str:
    """
    Hash le mot de passe avec Argon2
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si le mot de passe correspond au hash
    """
    return pwd_context.verify(plain_password, hashed_password)

# ==============================
# Fonctions JWT
# ==============================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Décode un token JWT et retourne les données
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Token invalide: {e}")