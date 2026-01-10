from langchain.agents.middleware import after_model

@after_model
def response_validator_middleware(state, runtime):
    """
    Valide et nettoie la réponse pour que l'utilisateur ne voie que du contenu professionnel.
    """
    messages = state.get("messages", [])
    if not messages:
        return state

    last_message = messages[-1]
    response = (last_message.content or "").strip()

    if not response:
        last_message.content = "Sorry, I couldn't generate a valid response. Could you rephrase?"
        return state

    forbidden_phrases = [
        "i am an ai",
        "as an ai",
        "i cannot answer",
        "i am a professional ai",
        "i do not have feelings",
        "i do not have emotions",
        "designed to provide",
        "I'm functioning well as a professional AI designed",
        
    ]

    response_lower = response.lower()

    if any(phrase in response_lower for phrase in forbidden_phrases):
        # Générer une version neutre et professionnelle
        last_message.content = "I'm happy to help with that. Here's the information you need:"
    else:
        last_message.content = response

    return state
