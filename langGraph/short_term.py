# Installer LangGraph si ce n'est pas déjà fait
# pip install langgraph langchain langchain-ollama

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, MessagesState
from langchain.messages import HumanMessage
from langchain_ollama import ChatOllama

# 1️⃣ Initialiser le modèle (ici Mistral via Ollama)
model = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434"
)

# 2️⃣ Créer le checkpointer pour sauvegarder l'état en mémoire (court terme)
checkpointer = InMemorySaver()

# 3️⃣ Définir la fonction du modèle
def call_model(state: MessagesState):
    # Appel du modèle avec les messages de l'état
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# 4️⃣ Construire le graphe
builder = StateGraph(MessagesState)
builder.add_node(call_model)
builder.add_edge(START, "call_model")

graph = builder.compile(checkpointer=checkpointer)

# 5️⃣ Configurer le thread (conversation)
config = {"configurable": {"thread_id": "1"}}

# 6️⃣ Envoyer des messages
graph.invoke({"role":"user", "messages": [HumanMessage(content="Hi! My name is Bob")]}, config)
graph.invoke({"role":"user", "messages": [HumanMessage(content="What's my name?")]}, config)

# 7️⃣ Afficher l'état actuel (mémoire à court terme)
state_snapshot = graph.get_state(config)
print("\n--- Current State ---")
for msg in state_snapshot.values['messages']:
    print(f"{msg.type}: {msg.content}")

# 8️⃣ Afficher l'historique complet
history = list(graph.get_state_history(config))
print("\n--- Full History ---")
for i, snapshot in enumerate(history):
    messages = [f"{msg.type}: {msg.content}" for msg in snapshot.values['messages']]
    print(f"Step {i}: {messages}")