
import sys
import os
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.runtime import Runtime
from app.agent.context import Context
from app.agent.long_memory import load_profile, store
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.rag.get_document_reterived import retrieve_user_documents

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


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    runtime: Runtime[Context] = request.runtime
    user_id = runtime.context.user_id
    image_text = runtime.context.image_text or None
    pdf_name = runtime.context.pdf_name

    # Charger le profil utilisateur
    user_profile = load_profile(store, user_id)
    profile_context = user_profile.model_dump_json(indent=2)
    print(f"loaded profile context: {profile_context}")
    # Récupérer la dernière question de l'utilisateur
    user_messages = [m for m in request.messages if m.type == "human"]
    question = user_messages[-1].content.strip() if user_messages else ""

    # Historique conversationnel
    conversation_history = "\n".join(
        [f"{m.type.upper()}: {m.content}" for m in request.messages[-10:]]
    )

    # Récupérer documents RAG seulement si question est présente
    if question:
        docs_with_scores = retrieve_user_documents(user_id, question, pdf_name=pdf_name)
        if docs_with_scores:
                display_results(docs_with_scores)
                documents_context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores])
        else:
                # Aucun document trouvé → message par défaut
                return "I don't have any answer."
        
        documents_context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores]) if docs_with_scores else ""
    else:
        documents_context = ""

    # Construire prompt final
    return f"""
You are a professional AI assistant. Your goal is to provide **accurate, concise, and filtered answers** to the user's question. 

### 🔹 Important Instructions:
1. Focus **ONLY on answering the user's query**. Do not include irrelevant information or the raw context.  
2. Use the following sources to reason and support your answer:
   - 👤 User Profile: personalize explanation based on the user's skills, preferences, and goals.
   - 🖼️ Image Text: if available, use it as reference, but **integrate and summarize**, do not quote verbatim.
   - 📄 Retrieved Documents (RAG): only if a query is present, **filter and synthesize information**, do not copy-paste.
   - 🧠 Conversation History: for continuity and avoiding contradictions.

3. **Always filter and synthesize**: produce a coherent, professional answer.  
4. **Explain reasoning if useful**, then provide the final answer.  
5. Do **not hallucinate**, do not invent facts, and do not mention internal systems.

### Query:
{question or 'No question provided'}

### Image Text (reference):
{image_text or 'No image provided'}

### Retrieved Documents (reference):
{documents_context or 'No documents found'}

### Conversation History:
{conversation_history or 'No conversation history'}

### User Profile:
{profile_context}

Generate a **concise, professional, and filtered answer** that directly addresses the query, using all relevant context intelligently.
"""
