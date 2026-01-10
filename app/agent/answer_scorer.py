from langchain.agents.middleware import after_model
import re

# ─────────────────────────────────────────────
# INTENT DETECTION
# ─────────────────────────────────────────────
GREETING_PATTERNS = [
    r"\bhello\b", r"\bhi\b", r"\bhey\b",
    r"\bgood (morning|afternoon|evening)\b",
    r"\bhow are you\b"
]

SMALL_TALK_PATTERNS = [
    r"\bok\b", r"\byes\b", r"\bno\b", r"\bthanks?\b",
    r"\bdone\b", r"\bokay\b", r"\bhello [a-z]+\b"
]

def matches_any(patterns, text: str) -> bool:
    text = text.lower()
    return any(re.search(p, text) for p in patterns)

def is_low_content_expected(response: str) -> bool:
    """
    Detect greetings or short expected conversation responses
    """
    response = response.strip()
    return (
        matches_any(GREETING_PATTERNS, response)
        or matches_any(SMALL_TALK_PATTERNS, response)
        or len(response) <= 80  # short conversation is normal
    )

def is_task_response(runtime) -> bool:
    """
    Only responses related to tasks (PDF, Image, RAG) are scored
    """
    ctx = runtime.context
    return bool(ctx.pdf_name or ctx.image_text)

def detect_failure_modes(text: str):
    issues = []
    text_lower = text.lower()
    if "i am" in text_lower or "i cannot" in text_lower:
        issues.append("self_reference_or_refusal")
    if len(text.split()) < 20:
        issues.append("under_answer")
    return issues

# ─────────────────────────────────────────────
# QUALITY SCORER (INTERNE)
# ─────────────────────────────────────────────
@after_model
def answer_quality_scorer_middleware(state, runtime):
    """
    Middleware pour scorer la réponse en interne.
    ⚠️ Ne modifie jamais la réponse visible par l'utilisateur.
    """
    messages = state.get("messages", [])
    if not messages:
        return state

    response = messages[-1].content or ""
    clean_response = response.strip()

    # Ignorer les greetings ou petits messages
    if is_low_content_expected(clean_response):
        state.setdefault("internal_scoring", []).append({
            "type": "info",
            "reason": "short_conversation",
            "length": len(clean_response)
        })
        return state

    if not is_task_response(runtime):
        state.setdefault("internal_scoring", []).append({
            "type": "info",
            "reason": "not_task_response"
        })
        return state

    # Scoring des réponses de tâches
    problems = []
    if len(clean_response) < 120:
        problems.append("too_short")
    if len([l for l in clean_response.split("\n") if l.strip()]) < 4:
        problems.append("not_structured")
    issues = detect_failure_modes(clean_response)

    # Stocker les problèmes en interne
    if problems or issues:
        state.setdefault("internal_scoring", []).append({
            "type": "warning",
            "problems": problems,
            "issues": issues
        })

    return state
