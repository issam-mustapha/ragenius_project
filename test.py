from langchain_ollama import OllamaEmbeddings
model = "nomic-embed-text"
# Crée l'objet embeddings avec le modèle gratuit 'embed'
embeddings = OllamaEmbeddings(model="nomic-embed-text")

text = "Bonjour, je veux transformer ce texte en vecteur numérique"
vector = embeddings.embed_query(text)

print(vector)
print(len(vector))
