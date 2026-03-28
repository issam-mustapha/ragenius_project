import sys
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.agent.long_memory import build_long_memory_graph, load_profile, store

# Construire le graphe de mémoire long terme
long_memory_graph = build_long_memory_graph()

# Simuler un utilisateur
user_id = "1"

print("🧪 Test Long-Term Memory")
print("Tape 'exit' pour quitter.\n")

while True:
    user_input = input("👤 User: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Fin du test")
        break

    # 1️⃣ Envoyer le message dans le graphe long-term
    config = {"configurable": {"user_id": user_id, "thread_id": f"user-{user_id}"}}
    messages = {"messages": [{"role": "user", "content": user_input}]}

    for chunk in long_memory_graph.stream(messages, config, stream_mode="values"):
        response_messages = chunk["messages"]
        # Afficher la réponse de l'assistant
        print("🤖 Assistant:", response_messages[-1].content)

    # 2️⃣ Vérifier le profil en base
    profile = load_profile(store, user_id)
    print("\n📌 PROFIL EN BASE:")
    print(profile.model_dump_json(indent=2))
    print("-" * 50)
