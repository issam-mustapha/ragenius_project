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

# ─────────────────────────────────────────────
# QUALITY SCORER
# ─────────────────────────────────────────────
@after_model
def answer_quality_scorer_middleware(state, runtime):
    messages = state.get("messages", [])
    if not messages:
        return state

    response = messages[-1].content or ""
    clean_response = response.strip()
    lines = [l for l in clean_response.split("\n") if l.strip()]

    # 🟢 CASE 1: low-content / greeting / small talk → ignore
    if is_low_content_expected(clean_response):
        return state

    # 🟢 CASE 2: not a task response → ignore
    if not is_task_response(runtime):
        return state

    # 🟡 CASE 3: task response → quality check
    problems = []

    if len(clean_response) < 120:
        problems.append("too short")

    if len(lines) < 4:
        problems.append("not structured")

    if problems:
        messages[-1].content += (
            "\n\n⚠️ The response may be incomplete or insufficiently detailed."
        )

    return state
