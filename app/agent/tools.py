from langchain.tools import tool, ToolRuntime
from app.agent.context import Context

from PIL import Image
from app.agent.storage_utils import save_user_image, ocr_image  # ou adapte le chemin si utils séparé


@tool
def extract_text_from_user_image(runtime: ToolRuntime[Context], file_bytes: bytes, filename: str = None) -> str:
    """
    Stocke l'image de l'utilisateur, puis extrait le texte via OCR.
    """
    user_id = runtime.context.user_id

   
 
    image_path = save_user_image(user_id, file_bytes, filename)

   
    text = ocr_image(image_path)
    return text

@tool
def answer_based_on_image(runtime: ToolRuntime[Context], file_bytes: bytes, query: str, filename: str = None) -> str:
    """
    Stocke l'image, extrait le texte, puis combine avec la query pour l'agent.
    """
    user_id = runtime.context.user_id

    
    image_path = save_user_image(user_id, file_bytes, filename)

    
    image_text = ocr_image(image_path)

    
    combined_query = f"User query: {query}\nText extracted from image: {image_text}"

    return combined_query

