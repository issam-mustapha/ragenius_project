from langchain.agents.middleware import after_model

@after_model
def response_validator_middleware(state, runtime):
    """
    Validates and sanitizes the model's final response
    to ensure professional and user-facing quality.
    """

    messages = state.get("messages", [])
    if not messages:
        return state

    last_message = messages[-1]
    response = (last_message.content or "").strip()

    if not response:
        last_message.content = "⚠️ No valid response could be generated."
        return state

    forbidden_phrases = [
        "i am an ai",
        "as an ai",
        "i cannot answer",
        "i am a professional ai",
        "i do not have feelings",
        "i do not have emotions",
        "designed to provide",
    ]

    response_lower = response.lower()

    if any(phrase in response_lower for phrase in forbidden_phrases):
        last_message.content = (
            "The agent could not generate a valid professional response. "
            "Please rephrase your request."
        )
    else:
        last_message.content = response

    return state
