from pydantic import BaseModel, EmailStr
from typing import Optional
class UserCreate(BaseModel):
    nom: str
    prenom: str
    adress: str
    email: EmailStr
    mot_de_passe: str
    role: str = "user"

class UserOut(BaseModel):
    id: int
    nom: str
    prenom: str
    email: EmailStr
    role: str
class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str


    model_config = {
        "from_attributes": True
    }

class Token(BaseModel):
    access_token: str
    token_type: str
   

class ChatRequest(BaseModel):
    message: str
    guest_id: str | None = None  # facultatif si c'est un invité


class ChatResponse(BaseModel):
    reply: str

