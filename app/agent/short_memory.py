from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware

def get_checkpointer():
    return InMemorySaver()

def get_summarizer():
    return SummarizationMiddleware(
        model="mistral",
        trigger=("tokens", 3000),
        keep=("messages", 10)
    )
