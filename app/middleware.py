import uuid
from fastapi import Request

async def guest_user_middleware(request: Request, call_next):
    token = request.headers.get("Authorization")

    if token:
        # Ici tu récupères user_id depuis le token
        request.state.user_id = get_user_id_from_token(token)
    else:
        # Générer un guest_user_id unique avec préfixe "guest-"
        request.state.user_id = f"guest-{uuid.uuid4()}"

    response = await call_next(request)
    return response

# Exemple de fonction pour décoder token
def get_user_id_from_token(token: str) -> str:
    # Implémente ton décodage JWT ici
    # return user_id extrait du token
    return "user_from_token"
