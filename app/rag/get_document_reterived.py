import os
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

MODEL_NAME = "nomic-embed-text"

def get_user_vectorstore(user_id: int):
    """
    Retourne le vector store spécifique d'un utilisateur
    """
    user_db_dir = f"storage/users/user_{user_id}/vectordb"
    os.makedirs(user_db_dir, exist_ok=True)  # crée le dossier si pas existant

    embeddings = OllamaEmbeddings(model=MODEL_NAME)

    # Crée ou charge le vector store
    db = Chroma(
        persist_directory=user_db_dir,
        embedding_function=embeddings
    )
    return db

def retrieve_user_documents(user_id: int, query: str, k: int = 5, min_score: float = 0.8):
    """
    Retourne les documents pertinents pour la query de l'utilisateur
    """
    db = get_user_vectorstore(user_id)
    results = db.similarity_search_with_score(query, k=k)

    # Filtrer selon le score
    filtered = [(doc, score) for doc, score in results if score >= min_score]
    
    return filtered