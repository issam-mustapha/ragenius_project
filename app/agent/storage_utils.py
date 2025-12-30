import os
from datetime import datetime
import cv2
import pytesseract
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
pytesseract.pytesseract.tesseract_cmd = r"C:\ocr\tesseract.exe"

def clean_text(text: str) -> str:
    """
    Nettoie le texte OCR :
    - Supprime les retours à la ligne multiples
    - Supprime les espaces en trop
    - Supprime les caractères non imprimables
    """
    # Supprimer les caractères non imprimables
    text = re.sub(r'[^\x20-\x7EàâçéèêëîïôûùüÿñæœÀÂÇÉÈÊËÎÏÔÛÙÜŸÑÆŒ\n]', '', text)
    # Remplacer les retours à la ligne multiples par un seul espace
    text = re.sub(r'\s+', ' ', text)
    # Supprimer les espaces en début et fin
    text = text.strip()
    return text

def ocr_image(image_path: str) -> str:
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "Erreur : image non trouvée."
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text = pytesseract.image_to_string(gray, lang="eng+fra")
        # Nettoyer le texte
        return clean_text(text)
    except Exception as e:
        return f"Erreur OCR : {e}"
    
def save_user_image(user_id: int, file_bytes: bytes, filename: str = None) -> str:
    """
    Sauvegarde l'image dans le dossier spécifique à l'utilisateur
    et retourne le chemin complet du fichier.
    """
    user_image_dir = os.path.join(BASE_DIR, "storage", "users", f"user_{user_id}", "images")
    os.makedirs(user_image_dir, exist_ok=True)

    # Nommer le fichier si pas fourni
    if not filename:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"image_{timestamp}.png"

    file_path = os.path.join(user_image_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return file_path
