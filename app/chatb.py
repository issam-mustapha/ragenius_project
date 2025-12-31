import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Dossier courant :", os.getcwd())
from app.chat.service import chat_with_agent
def main():
    print("🤖 RAG CHATBOT (CLI)")
    user_id = "guest-4dee6efc-2838-463c-885b-d678df8c9b2b"

    while True:
        user_input = input("\n🧑 User > ")

        if user_input.lower() in {"exit", "quit"}:
            break

        response = chat_with_agent(user_id, user_input)
        print(f"\n🤖 Assistant > {response}")

if __name__ == "__main__":
    main()