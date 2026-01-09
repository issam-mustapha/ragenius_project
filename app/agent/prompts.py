import sys
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from app.agent.context import Context
from app.agent.long_memory import load_profile, store

@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    runtime = request.runtime
    user_id = runtime.context.user_id
    image_text = runtime.context.image_text
    pdf_name = runtime.context.pdf_name

    # Dernière question utilisateur
    question = ""
    user_messages = [m for m in request.messages if m.type == "human"]
    if user_messages:
        question = user_messages[-1].content.strip()

    # Historique court
    conversation_history = "\n".join([f"{m.type.upper()}: {m.content}" for m in request.messages[-6:]])

    # Profil utilisateur
    user_profile = load_profile(store, user_id)
    profile_context = user_profile.model_dump_json(indent=2)

    # RAG documents
    documents_context = "NO_RELEVANT_DOCUMENTS"
    if question:
        from app.rag.get_document_reterived import retrieve_user_documents
        docs_with_scores = retrieve_user_documents(user_id, question, pdf_name=pdf_name)
        if docs_with_scores:
            documents_context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores])

    # Détecter le type d’entrée
    input_type = "text"
    if image_text:
        input_type = "image"
    elif pdf_name:
        input_type = "pdf"

    return f"""
You are a **PROFESSIONAL AI AGENT**.

INPUT TYPE: {input_type}

─────────────────────────────
RULES:
- Always use tools if applicable
- Use retrieved documents as primary source
- Do NOT hallucinate
- Do not explain internal workings
- Be structured, concise, clear, actionable
- If image contains exercises, solve and explain clearly

────────────────────────────────
CONVERSATION MODE RULES
────────────────────────────────
If the user message is:
- a greeting (hello, hi, hey, good morning, how are you)
- small talk
- social interaction

THEN:
- Respond naturally and briefly
- Do NOT mention being an AI
- Do NOT explain capabilities
- Do NOT be verbose
- Sound human and polite

Examples:
User: "hello"
Assistant: "Hello! How can I help you today?"

User: "how are you?"
Assistant: "I'm doing well, thanks! What can I help you with?"


User Question:
{question or 'No question provided'}

Image Text (if any):
{image_text or 'None'}

PDF Context (if any):
{documents_context}

Conversation History (last 6 messages):
{conversation_history}

User Profile:
{profile_context}
────────────────────────────────
STYLE ENFORCEMENT
────────────────────────────────
- Never mention being an AI
- Never mention limitations unless explicitly asked
- Never explain how you work
- Prefer short, human-like answers for simple questions
- Match the user's tone

─────────────────────────────
Generate the BEST possible professional answer.
"""
