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
    
    text = re.sub(r'[^\x20-\x7EàâçéèêëîïôûùüÿñæœÀÂÇÉÈÊËÎÏÔÛÙÜŸÑÆŒ\n]', '', text)
  
    text = re.sub(r'\s+', ' ', text)
  
    text = text.strip()
    return text

def remove_redundant_phrases(text: str) -> str:
    # Supprime les phrases répétées consécutivement
    lines = text.split('. ')
    seen = set()
    cleaned_lines = []
    for line in lines:
        if line not in seen:
            cleaned_lines.append(line)
            seen.add(line)
    return '. '.join(cleaned_lines)

def ocr_image(image_path: str) -> str:
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "Erreur : image non trouvée."
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text = pytesseract.image_to_string(gray, lang="eng+fra")
        cleaned_text = clean_text(text)
        cleaned_text = remove_redundant_phrases(cleaned_text)
        # Nettoyer le texte
        return cleaned_text
    except Exception as e:
        return f"Erreur OCR : {e}"
    
def save_user_image(user_id: int, file_bytes: bytes, filename: str = None) -> str:
    """
    Sauvegarde l'image dans le dossier spécifique à l'utilisateur
    et retourne le chemin complet du fichier.
    """
    user_image_dir = os.path.join(BASE_DIR, "storage", "users", f"user_{user_id}", "images")
    os.makedirs(user_image_dir, exist_ok=True)

   
    if not filename:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"image_{timestamp}.png"

    file_path = os.path.join(user_image_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return file_path
