# chat_cli.py
import sys
import os

# Remonter vers la racine du projet (projet 3 docker)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Importer la fonction chatbot
from app.chat.chatbot import chat_with_agent   # adapte le chemin si besoin


def main():
    print("=" * 60)
    print("🤖 RAG CHATBOT - MODE INTERACTIF (CLI)")
    print("Tape 'exit' ou 'quit' pour quitter")
    print("=" * 60)

    # 🔐 Simuler un utilisateur connecté
    user_id = 6

    while True:
        try:
            user_input = input("\n🧑 User > ")

            if user_input.lower() in {"exit", "quit"}:
                print("\n👋 Fin de la conversation. À bientôt !")
                break

            # Appel à ton agent avec mémoire
            response = chat_with_agent(
                user_id=user_id,
                query=user_input
            )

            print(f"\n🤖 Assistant > {response}")

        except KeyboardInterrupt:
            print("\n\n👋 Arrêt manuel (CTRL+C)")
            break

        except Exception as e:
            print(f"\n❌ Erreur : {e}")


if __name__ == "__main__":
    main()
