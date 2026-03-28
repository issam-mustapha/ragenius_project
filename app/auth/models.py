from sqlalchemy import Column, Integer, String, ForeignKey,JSON, DateTime, Text, func
from app.connexion_db import Base
from sqlalchemy.orm import relationship

from app.connexion_db import Base

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
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

class PdfDocument(Base):
    __tablename__ = "pdf_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="pdfs")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="Nouvelle conversation")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String, nullable=False)  # 'user' ou 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation
    conversation = relationship("Conversation", back_populates="messages")

