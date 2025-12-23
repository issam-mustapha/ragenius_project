import sys
import os
from dataclasses import dataclass
from langchain_ollama import ChatOllama
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model, SummarizationMiddleware
from langgraph.runtime import Runtime
from langchain.messages import HumanMessage
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

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

# Mémoire court terme (en RAM)
checkpointer = InMemorySaver()

# =========================
# Contexte utilisateur simplifié
# =========================
@dataclass
class Context:
    user_id: int

# =========================
# Dynamic system prompt
# =========================
summarizer = SummarizationMiddleware(
    model="mistral",        # ou mistral:latest si dispo
    trigger=("tokens", 3000),  # résumer quand on dépasse
    keep=("messages", 10)      # garder les 10 derniers messages
)

@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    runtime: Runtime[Context] = request.runtime
    user_id = runtime.context.user_id

    user_messages = [m for m in request.messages if m.type == "human"]
    question = user_messages[-1].content if user_messages else ""

    docs_with_scores = retrieve_user_documents(user_id, question)
    rag_prompt = ""
    if docs_with_scores:
        context_text = "\n\n".join([doc.page_content for doc, score in docs_with_scores])
        print(f"the context text {context_text}")
        rag_prompt = f"""
You should use the following documents:
{context_text}
"""
    system_prompt = f"""
You are a professional conversational assistant.

Rules:
- You can use conversation memory to answer questions.
- Use documents if the answer is not in conversation memory .
- If the user shared personal information earlier (like their name), remember it.
- Do NOT say "I don't have information" if the answer is in the conversation history.

{rag_prompt}
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

@tool
def fetch_user_email_preferences(runtime: ToolRuntime[Context]) -> str:  
    """Fetch the user's email preferences from the store."""
    user_id = runtime.context.user_id  
    preferences: str = "The user prefers details in response."
    if runtime.store:  
        if memory := runtime.store.get(("users",), user_id):  
            preferences = memory.value["preferences"]

    return preferences

agent = create_agent(
    model=model,
    tools=[fetch_user_email_preferences],  # Ajouter des outils plus tard si nécessaire
    middleware=[summarizer,dynamic_system_prompt, log_before_model, log_after_model],
    context_schema=Context,
    checkpointer=checkpointer   # ✅ mémoire activée
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
    config: RunnableConfig = {
        "configurable": {
            "thread_id": f"user-{user_id}"  # 🧠 mémoire par utilisateur
        }
    }
    # Invoquer l'agent
    response = agent.invoke(
        {"messages": messages},
        context=runtime_context,
        config=config
    )

    ai_messages = [m for m in response["messages"] if m.type == "ai"]

    # fallback
    return ai_messages[-1].content if ai_messages else "No response."