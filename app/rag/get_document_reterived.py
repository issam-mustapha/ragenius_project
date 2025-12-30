import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

MODEL_NAME = "nomic-embed-text"
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
def get_user_vectorstore(user_id: int):
    """
    Retourne le vector store spécifique d'un utilisateur
    """
    user_db_dir = os.path.join(
    BASE_DIR,
    "storage",
    "users",
    f"user_{user_id}",
    "vectordb"
)
   
    embeddings = OllamaEmbeddings(model=MODEL_NAME)

    # Crée ou charge le vector store
    db = Chroma(
        persist_directory=user_db_dir,
        embedding_function=embeddings
    )
    return db

def retrieve_user_documents(
    user_id: int,
    query: str,
    k: int = 5,
    pdf_name: str | None = None,
    min_score: float = 0.8
):
    """
    Retourne les documents pertinents pour la query de l'utilisateur
    (avec filtre optionnel par PDF)
    """
    db = get_user_vectorstore(user_id)

    search_kwargs = {"k": k}

    # 🔥 FILTRE PAR PDF (IMPORTANT)
    if pdf_name:
        search_kwargs["filter"] = {
            "source": pdf_name
        }

    results = db.similarity_search_with_score(
        query,
        **search_kwargs
    )

    # Filtrer selon le score
    filtered = [(doc, score) for doc, score in results if score >= min_score]

    return filtered

results = retrieve_user_documents(
    user_id=2,
    query="what's machine learning?",
    #pdf_name="pdfee.pdf"
)
def display_results(results):
    if not results:
        print("❌ Aucun document pertinent trouvé.")
        return

    print("\n📚 Résultats trouvés :\n" + "-" * 40)

    for i, (doc, score) in enumerate(results, start=1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", None)

        page_display = f"Page {page + 1}" if page is not None else "Page ?"

        print(f"🔹 Résultat {i}")
        print(f"📄 Document : {source}")
        print(f"📑 {page_display}")
        print(f"🎯 Score : {score:.2f}")
        print(f"📝 Extrait : {doc.page_content[:200]}...")
        print("-" * 40)
#display_results(results)