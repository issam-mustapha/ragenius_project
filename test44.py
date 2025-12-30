import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\ocr\tesseract.exe"
image_path = r"D:\workspace langChain\projet 3 docker\upload\test2.jpg"

img = Image.open(image_path)

# OCR sans spécifier de langue
text = pytesseract.image_to_string(img)

print("Texte extrait :")
print(repr(text))  # repr pour voir s'il y a des retours à la ligne ou espaces
