
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.rag.get_document_reterived import retrieve_user_documents
print("Dossier courant :", os.getcwd())


docs_with_scores = retrieve_user_documents(1, "who is rachid alyachi")
documents_context = ""
if docs_with_scores:
        documents_context = "\n\n".join(
            [doc.page_content for doc, score in docs_with_scores]
        )
        print(f"les documents de contexts sont {documents_context}")
else:
        print("No documents found.") 