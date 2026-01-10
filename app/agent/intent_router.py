import re
from dataclasses import dataclass

@dataclass
class Intent:
    type: str
    confidence: float

def detect_intent(text: str, context) -> Intent:
    t = text.lower().strip()

    if re.match(r"^(hi|hello|hey|good morning|how are you)", t):
        return Intent("greeting", 0.95)

    if any(k in t for k in ["summarize", "resume", "explain pdf"]):
        return Intent("pdf_task", 0.9)

    if context.image_text:
        return Intent("image_task", 0.9)

    if any(k in t for k in ["about me", "my profile", "what do you know"]):
        return Intent("profile_query", 0.9)

    if len(t.split()) < 5:
        return Intent("small_talk", 0.7)

    return Intent("general_reasoning", 0.6)
