from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from app.agent.context import Context
from app.agent.agent_factory import build_agent
from app.agent.long_memory import build_long_memory_graph

# Construire agent et mémoire long terme
agent = build_agent()
long_memory_graph = build_long_memory_graph()

def chat_with_agent(user_id: int, query: str) -> str:
    if not query.strip():
        return "Query is empty."

    context = Context(user_id=user_id)
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