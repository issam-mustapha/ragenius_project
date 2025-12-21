from langchain_ollama import ChatOllama
from app.rag.get_document_reterived import retrieve_user_documents

model = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434"
)

def chat_with_rag(user_id: int, query: str):
    docs_with_scores = retrieve_user_documents(user_id, query)
    if not docs_with_scores:
     return "I don't have enough information in your documents to answer this question."

    # 🔥 correction ici
    context = "\n\n".join(
        [doc.page_content for doc, score in docs_with_scores]
    )

    prompt = f"""
    Use the following documents to answer the question.

    Documents:
    {context}

    Question:
    {query}

    """


    response = model.invoke(prompt)
    return response.content
