import os
import pickle
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

MODEL_NAME = "nomic-embed-text"
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

def get_user_vectorstore(user_id: int):
    user_db_dir = os.path.join(
        BASE_DIR,
        "storage",
        "users",
        f"user_{user_id}",
        "vectordb"
    )

    index_faiss = os.path.join(user_db_dir, "index.faiss")
    index_pkl = os.path.join(user_db_dir, "index.pkl")

    if not os.path.exists(index_faiss):
        print("❌ FAISS index not found")
        return None, []

    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    db = FAISS.load_local(
        user_db_dir,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db, db.docstore._dict.values()



def retrieve_user_documents(
    user_id: int,
    query: str,
    k: int = 5,
    pdf_name: str | None = None,
    max_distance: float = 1.5
):
    db, _ = get_user_vectorstore(user_id)
    if not db:
        return []

    results = db.similarity_search_with_score(query, k=k)

    filtered = []
    for doc, distance in results:
        if distance > max_distance:
            continue

        if pdf_name and doc.metadata.get("source") != pdf_name:
            continue

        filtered.append((doc, distance))

    return filtered


results = retrieve_user_documents(
    user_id=28,
    query="who is issam adoch",
    k=3
)

print("Results:", len(results))

for i, (doc, score) in enumerate(results, 1):
    print(f"\n===== DOCUMENT {i} =====")
    print(f"Score (distance): {score}")
    print("Source PDF:", doc.metadata.get("source"))
    print("Page:", doc.metadata.get("page"))
    print("User ID:", doc.metadata.get("user_id"))
    print("\n📄 CONTENU COMPLET :\n")
    print(doc.page_content)
    print("\n" + "=" * 80)




db, documents = get_user_vectorstore(user_id=28)

print("📊 FAISS index size:", db.index.ntotal if db else 0)
print("📄 Stored documents:", len(list(documents)))
