import os
import sys
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from app.agent.context import Context
from app.agent.agent_factory import build_agent
from app.agent.long_memory import build_long_memory_graph
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from auth.models import Conversation ,Message

QUALITY_WARNING = "⚠️ The response may be incomplete or insufficiently detailed."
agent = build_agent()
long_memory_graph = build_long_memory_graph()




def clean_ai_response(text: str) -> str:
    if not text:
        return text
    return text.replace(QUALITY_WARNING, "").strip()




def chat_with_agent(user_id: int, query: str | None = None , image_text: str | None = None , pdf_name: str | None = None) -> str:
    if (not query or not query.strip()) and image_text:
        query = "Analyze the text extracted from the image and answer accordingly."

    # 🔹 Si toujours vide → erreur
    if not query or not query.strip():
        return "Please provide a question or an image."

    context = Context(user_id=user_id, image_text=image_text, pdf_name=pdf_name)
    messages = [HumanMessage(content=query)]
    config: RunnableConfig = {
        "configurable": {
            "thread_id": f"user-{user_id}",
            "user_id": str(user_id)  # pour long-term memory
        }
    }

    # 1️⃣ Mettre à jour la mémoire long terme
    long_memory_graph.stream({"messages": [{"role": "user", "content": query}]}, config, stream_mode="ignore")

    # 2️⃣ Appeler l’agent RAG (short-term memory)
    response = agent.invoke(
        {"messages": messages},
        context=context,
        config=config
    )

    ai_messages = [m for m in response["messages"] if m.type == "ai"]
    return ai_messages[-1].content if ai_messages else "No response."







def get_or_create_conversation(
    db: Session,
    user_id: str,
    conversation_id: Optional[int],
    first_message: str
) -> Conversation:
    """
    Récupère une conversation existante si elle appartient à l'utilisateur,
    sinon crée une nouvelle conversation.
    """

    # 🔹 Cas utilisateur authentifié
    if not user_id.startswith("guest-") and conversation_id:
        conv = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            .first()
        )

        if conv:
            return conv
    # 🔹 Créer une nouvelle conversation
    title = first_message[:50] if first_message else "Nouvelle conversation"

    conv = Conversation(
        user_id=user_id,
        title=title
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str
):
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(msg)
    db.commit()

def get_user_conversations(db: Session, user_id: int):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )







def get_conversation_with_messages(
    db: Session,
    conversation_id: int,
    user_id: int
):
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        .first()
    )

def get_messages_paginated(
    db: Session,
    conversation_id: int,
    user_id: int,
    limit: int = 20,
    offset: int = 0
):
    return (
        db.query(Message)
        .join(Conversation)
        .filter(
            Message.conversation_id == conversation_id,
            Conversation.user_id == user_id
        )
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

