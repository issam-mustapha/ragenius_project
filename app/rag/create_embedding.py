import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

MODEL_NAME = "nomic-embed-text"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def create_user_embeddings(user_id: int):
    user_pdf_dir = f"storage/users/user_{user_id}/pdfs"
    user_db_dir = f"storage/users/user_{user_id}/vectordb"

    os.makedirs(user_db_dir, exist_ok=True)

    # Charger DB existante si elle existe
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    db = Chroma(persist_directory=user_db_dir, embedding_function=embeddings)

    # Lister tous les PDFs uploadés
    pdf_files = [f for f in os.listdir(user_pdf_dir) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"⚠️ User {user_id} has no PDFs")
        return None

    # Récupérer les PDFs déjà présents dans la vectordb
    existing_sources = set()
    if db._collection:
        # db._collection.get()["metadatas"] contient les sources
        metadatas = db._collection.get()["metadatas"]
        for meta in metadatas:
            if "source" in meta and meta["source"]:
                existing_sources.add(meta["source"])

    print(f"les pdfs de cet user est {existing_sources}")
    # Filtrer les PDF qui n'ont pas encore été traités
    new_pdfs = [pdf for pdf in pdf_files if pdf not in existing_sources]
    if not new_pdfs:
        print(f"✅ No new PDFs to process for user {user_id}")
        return db
    print(f"my new pdf is {new_pdfs}")
    documents = []
    for pdf in new_pdfs:
        loader = PyPDFLoader(os.path.join(user_pdf_dir, pdf))
        pages = loader.load()

        for page in pages:
                text = page.page_content.replace("\n", " ").strip()
                page.page_content = f"This section explains the following concept:\n{text}"
                page.metadata.update({
                "source": pdf,
                "page": page.metadata.get("page", None),  # numéro de page
                "user_id": user_id
    })
                documents.append(page)

    print(f"📄 Loaded {len(documents)} pages from {len(new_pdfs)} new PDFs")

    # Split en chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✂️ Created {len(chunks)} chunks for new PDFs")

    # Ajouter seulement les nouveaux chunks
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        db.add_documents(chunks[i:i+batch_size])
        print(f"🧠 Added {i+len(chunks[i:i+batch_size])}/{len(chunks)} chunks")

    #db.persist()
    print(f"✅ Vector store updated for user {user_id}")
    return db
