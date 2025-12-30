
import sys
import os
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.runtime import Runtime
from app.agent.context import Context
from app.agent.long_memory import load_profile, store
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.rag.get_document_reterived import retrieve_user_documents


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    runtime: Runtime[Context] = request.runtime
    user_id = runtime.context.user_id
    user_profile = load_profile(store, user_id)
    profile_context = user_profile.model_dump_json(indent=2)
    user_messages = [m for m in request.messages if m.type == "human"]
    question = user_messages[-1].content if user_messages else ""

    conversation_history = "\n".join(
        [f"{m.type.upper()}: {m.content}" for m in request.messages[-10:]]
    )

    docs_with_scores = retrieve_user_documents(user_id, question)

    documents_context = "\n\n".join(
        [doc.page_content for doc, _ in docs_with_scores]
    ) if docs_with_scores else "No relevant documents found."

    return f"""
You are a highly intelligent RAG conversational assistant.

### Conversation Memory
{conversation_history}

### Retrieved Documents
{documents_context}

### User Profile (long-term memory):
{profile_context}


### Rules:
- Prioritize documents if relevant
- Use conversation history for continuity
- Be clear, professional, and helpful
"""
