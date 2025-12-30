from langchain.tools import tool, ToolRuntime
from app.agent.context import Context
import pytesseract
import cv2
from PIL import Image
from app.agent.storage_utils import save_user_image, ocr_image  # ou adapte le chemin si utils séparé

@tool
def fetch_user_email_preferences(runtime: ToolRuntime[Context]) -> str:
    """Fetch user preferences"""
    user_id = runtime.context.user_id

    if runtime.store:
        if memory := runtime.store.get(("users",), user_id):
            return memory.value.get("preferences", "No preferences found")

    return "The user prefers detailed responses."

@tool
def extract_text_from_user_image(runtime: ToolRuntime[Context], file_bytes: bytes, filename: str = None) -> str:
    """
    Stocke l'image de l'utilisateur, puis extrait le texte via OCR.
    """
    user_id = runtime.context.user_id

    # 1️⃣ Stocker l'image dans le dossier utilisateur
 
    image_path = save_user_image(user_id, file_bytes, filename)

    # 2️⃣ Extraire le texte
    text = ocr_image(image_path)
    return text

@tool
def answer_based_on_image(runtime: ToolRuntime[Context], file_bytes: bytes, query: str, filename: str = None) -> str:
    """
    Stocke l'image, extrait le texte, puis combine avec la query pour l'agent.
    """
    user_id = runtime.context.user_id

    # 1️⃣ Stocker l'image
    image_path = save_user_image(user_id, file_bytes, filename)

    # 2️⃣ Extraire le texte
    image_text = ocr_image(image_path)

    # 3️⃣ Combiner avec la query
    combined_query = f"User query: {query}\nText extracted from image: {image_text}"

    return combined_query

