import os
import shutil

from app.rag.get_document_reterived import BASE_DIR
user_id=21
user_db_dir = os.path.join(
    BASE_DIR,  # par exemple: D:/workspace langChain/projet 3 docker
    "storage",
    "users",
    f"user_{user_id}",
    "vectordb"
)

# 🔹 Supprimer complètement le dossier existant (vectordb)
shutil.rmtree(user_db_dir, ignore_errors=True)

# 🔹 Recréer le dossier vide
os.makedirs(user_db_dir, exist_ok=True)

print(f"✅ Cleaned and recreated vectordb folder for user {user_id}")
