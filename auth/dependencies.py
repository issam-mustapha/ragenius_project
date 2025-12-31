from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from auth.models import User
from app.connexion_db import get_db
from auth.auth import SECRET_KEY, ALGORITHM
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="login",
    auto_error=False
)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    return user
def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
):
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.email == email).first()
    return user