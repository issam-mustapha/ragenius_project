from langchain_ollama import ChatOllama

def get_llm():
    return ChatOllama(
        model="mistral",
        base_url="http://localhost:11434"
    )
