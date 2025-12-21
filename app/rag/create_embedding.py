import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# ===============================
# CONFIG (OPTIMISÉE)
# ===============================
MODEL_NAME ="nomic-embed-text"   # 🔥 meilleur que nomic ici
CHUNK_SIZE = 120                   # 🔥 idéal pour définitions
CHUNK_OVERLAP = 30
TOP_K = 5
FETCH_K = 20                       # pour MMR

# ===============================
# PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_DIR = os.path.join(BASE_DIR, "books")
DB_DIR = os.path.join(BASE_DIR, "db", "chroma_db")

os.makedirs(DB_DIR, exist_ok=True)

# ===============================
# LOAD & CLEAN PDF
# ===============================
print("📄 Loading PDF files...")

documents = []

pdf_files = [f for f in os.listdir(BOOKS_DIR) if f.endswith(".pdf")]
if not pdf_files:
    raise RuntimeError("❌ No PDF files found in books/")

for pdf in pdf_files:
    loader = PyPDFLoader(os.path.join(BOOKS_DIR, pdf))
    pages = loader.load()

    for page in pages:
        clean_text = (
            page.page_content
            .replace("\n", " ")
            .replace("  ", " ")
            .strip()
        )

        # 🔥 enrichissement sémantique léger
        page.page_content = f"This section explains the following concept:\n{clean_text}"
        page.metadata["source"] = pdf

        documents.append(page)

print(f"✅ Loaded {len(documents)} pages")

# ===============================
# SPLIT DOCUMENTS (IMPORTANT)
# ===============================
print("✂️ Splitting documents...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)

chunks = text_splitter.split_documents(documents)
print(f"✅ Created {len(chunks)} chunks")

# ===============================
# VECTOR STORE
# ===============================
print("🧠 Creating vector store...")

embeddings = OllamaEmbeddings(model=MODEL_NAME)

db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DB_DIR
)

print("✅ Vector store ready")
