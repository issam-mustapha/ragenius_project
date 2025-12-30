from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from app.agent.context import Context
from app.agent.agent_factory import build_agent
from app.agent.long_memory import build_long_memory_graph

# Construire agent et mémoire long terme
agent = build_agent()
long_memory_graph = build_long_memory_graph()

def chat_with_agent(user_id: int, query: str | None = None , image_text: str | None = None) -> str:
    if (not query or not query.strip()) and image_text:
        query = "Analyze the text extracted from the image and answer accordingly."

    # 🔹 Si toujours vide → erreur
    if not query or not query.strip():
        return "Please provide a question or an image."

    context = Context(user_id=user_id, image_text=image_text)
    messages = [HumanMessage(content=query)]
    config: RunnableConfig = {
        "configurable": {
            "thread_id": f"user-{user_id}",
            "user_id": str(user_id)  # pour long-term memory
        }
    }

    # 1️⃣ Mettre à jour la mémoire long terme
    long_memory_graph.stream({"messages": [{"role": "user", "content": query}]}, config, stream_mode="ignore")

    # 2️⃣ Appeler l’agent RAG (short-term memory)
    response = agent.invoke(
        {"messages": messages},
        context=context,
        config=config
    )

    ai_messages = [m for m in response["messages"] if m.type == "ai"]
    return ai_messages[-1].content if ai_messages else "No response."