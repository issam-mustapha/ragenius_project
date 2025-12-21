import sys
import os
from dataclasses import dataclass
from langchain_ollama import ChatOllama
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model
from langgraph.runtime import Runtime
from langchain.messages import HumanMessage

# Remonte jusqu'au dossier "projet 3 docker"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
print("Dossier courant :", os.getcwd())
from app.rag.get_document_reterived import retrieve_user_documents
# =========================
# Définition du modèle
# =========================
model = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434"
)

# =========================
# Contexte utilisateur simplifié
# =========================
@dataclass
class Context:
    user_id: int

# =========================
# Dynamic system prompt
# =========================
@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    runtime: Runtime[Context] = request.runtime
    user_id = runtime.context.user_id

    # Accéder correctement au contenu du message
    if hasattr(request, "messages"):
        # request.messages est une liste de HumanMessage / AIMessage
        user_messages = [m for m in request.messages if m.type == "human"]
        question = user_messages[-1].content if user_messages else ""
    else:
        question = ""

    # Récupérer les documents pertinents
    docs_with_scores = retrieve_user_documents(user_id, question)

    if docs_with_scores:
        context_text = "\n\n".join([doc.page_content for doc, score in docs_with_scores])
        rag_prompt = f"Use the following documents to answer the question:\n{context_text}\n"
    else:
        rag_prompt = "I don't have enough information in your documents to answer this question.\n"

    system_prompt = f"""
    You are a professional assistant. Answer the user's question using the documents if available.
    {rag_prompt}
    Question: {question}
    """
    return system_prompt


# =========================
# Hooks avant/après modèle
# =========================
@before_model
def log_before_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    print(f"[BEFORE MODEL] Processing request for user_id: {runtime.context.user_id}")
    return None

@after_model
def log_after_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    print(f"[AFTER MODEL] Completed request for user_id: {runtime.context.user_id}")
    return None

# =========================
# Création de l'agent RAG pro
# =========================
agent = create_agent(
    model=model,
    tools=[],  # Ajouter des outils plus tard si nécessaire
    middleware=[dynamic_system_prompt, log_before_model, log_after_model],
    context_schema=Context
)
def chat_with_agent(user_id: int, query: str) -> str:
    """
    Cette fonction reçoit un user_id et une query,
    et retourne la réponse générée par l'agent RAG.
    """
    if not query.strip():
        return "Query is empty."

    # Créer un Runtime avec le contexte utilisateur
    runtime_context = Context(user_id=user_id)

    # Construire le message utilisateur pour l'agent
    messages = [HumanMessage(content=query)]

    # Invoquer l'agent
    response = agent.invoke(
        {"messages": messages},
        context=runtime_context
    )

  # Extraire uniquement le texte de l'AIMessage
    if hasattr(response, "messages"):
        ai_messages = [m for m in response.messages if m.type == "ai"]
        if ai_messages:
            return ai_messages[-1].content  # texte du dernier message AI
    # fallback
    return str(response)
