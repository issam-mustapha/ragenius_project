import os
import pickle
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS


MODEL_NAME = "nomic-embed-text"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def create_user_embeddings(user_id: int):
    user_pdf_dir = f"storage/users/user_{user_id}/pdfs"
    user_db_dir = f"storage/users/user_{user_id}/vectordb"

    os.makedirs(user_db_dir, exist_ok=True)

    index_path = os.path.join(user_db_dir, "faiss.index")
    store_path = os.path.join(user_db_dir, "docs.pkl")

    embeddings = OllamaEmbeddings(model=MODEL_NAME)

    # 🔹 Charger FAISS existant si présent
    if os.path.exists(index_path) and os.path.exists(store_path):
        db = FAISS.load_local(user_db_dir, embeddings, allow_dangerous_deserialization=True)
        with open(store_path, "rb") as f:
            existing_docs = pickle.load(f)
    else:
        db = None
        existing_docs = []

    # 🔹 PDFs existants
    existing_sources = {
        doc.metadata.get("source") for doc in existing_docs
        if "source" in doc.metadata
    }

    pdf_files = [f for f in os.listdir(user_pdf_dir) if f.endswith(".pdf")]
    new_pdfs = [pdf for pdf in pdf_files if pdf not in existing_sources]

    if not new_pdfs:
        print(f"✅ No new PDFs for user {user_id}")
        return db

    documents = []
    for pdf in new_pdfs:
        loader = PyPDFLoader(os.path.join(user_pdf_dir, pdf))
        pages = loader.load()

        for page in pages:
            text = page.page_content.replace("\n", " ").strip()
            page.page_content = f"This section explains the following concept:\n{text}"
            page.metadata.update({
                "source": pdf,
                "page": page.metadata.get("page"),
                "user_id": user_id
            })
            documents.append(page)

    print(f"📄 Loaded {len(documents)} pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)

    print(f"✂️ Created {len(chunks)} chunks")

    if db is None:
        db = FAISS.from_documents(chunks, embeddings)
        all_docs = chunks
    else:
        db.add_documents(chunks)
        all_docs = existing_docs + chunks

    # 💾 Sauvegarde
    db.save_local(user_db_dir)
    with open(store_path, "wb") as f:
        pickle.dump(all_docs, f)

    print(f"✅ FAISS vector store updated for user {user_id}")
    return db
