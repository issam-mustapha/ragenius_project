import os

from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
model_name="nomic-embed-text"



# Define the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "chroma_db")

# Define the embedding model
embeddings = OllamaEmbeddings(model=model_name)


# Load the existing vector store with the embedding function
db = Chroma(persist_directory=persistent_directory,
            embedding_function=embeddings)

# Define the user's question
query = "talk about War Room promotes of andrew tate"

# Retrieve relevant documents based on the query
def retrieve_context(query: str):
    results = db.similarity_search_with_score(query, k=5)

    filtered = [
        (doc, score) for doc, score in results if score > 0.8
    ]

    return filtered


relevant_docs = retrieve_context(query)

print("\n--- Relevant Documents ---")

if not relevant_docs:
    print("❌ Aucun document pertinent trouvé")
else:
    for i, (doc, score) in enumerate(relevant_docs, 1):
        print(f"Document {i}")
        print(f"Similarity score: {score:.4f}")
        print(doc.page_content)
        print(f"Metadata: {doc.metadata}")
        print("=" * 90)
