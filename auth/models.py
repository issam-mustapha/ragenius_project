from sqlalchemy import Column, Integer, String, ForeignKey,JSON
from app.connexion_db import Base
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    adress = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mot_de_passe = Column(String, nullable=False)
    role = Column(String, default="user")

    pdfs = relationship("PdfDocument", back_populates="user")
    preference = relationship(
        "UserPreference",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan"
    )

class PdfDocument(Base):
    __tablename__ = "pdf_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="pdfs")



class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    preferences = Column(JSON, nullable=False, default={
        "response_style": "detailed",
        "language": "en",
        "tone": "professional",
        "use_rag": True
    })

    user = relationship("User", back_populates="preference")
