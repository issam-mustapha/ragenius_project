import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.rag.get_document_reterived import retrieve_user_documents

# Récupération des documents
docs = retrieve_user_documents(6, "who is issam")

# Vérifier si des documents ont été trouvés
if not docs:
    print({"message": "Aucun document pertinent trouvé", "results": []})
else:
    # Formater la réponse
    results = []
    for doc, score in docs:
        results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "similarity_score": score
        })

    print({"results": results})

    # Afficher le contenu pour debug
    print(f"Documents found: {len(docs)}")
    for doc, score in docs:
        print(doc.page_content, score)
