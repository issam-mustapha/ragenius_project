import uuid
from fastapi import Request
from jose import jwt, JWTError, ExpiredSignatureError
from auth.dependencies import SECRET_KEY, ALGORITHM

async def guest_user_middleware(request: Request, call_next):
    """
    Middleware pour gérer utilisateur connecté ou guest.
    - Si Authorization Bearer token présent → extraire user_id du token
    - Sinon → générer guest user_id unique
    """
    token = request.headers.get("Authorization")
    
    user_id = None

    if token:
        
        try:
            token_value = token.split(" ")[1]
            
        except IndexError:
            token_value = token
        user_id = get_user_id_from_token(token_value)


    if not user_id:
        
        user_id = f"guest-{uuid.uuid4()}"

    request.state.user_id = user_id
    response = await call_next(request)
    return response



from jose import jwt, JWTError, ExpiredSignatureError

def get_user_id_from_token(token: str) -> str:
    """
    Décode le token JWT et retourne le user_id (sub) sous forme de string.
    Lève JWTError si le token est invalide.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise JWTError("Le token ne contient pas de 'sub'")
        return str(user_id)  
    except ExpiredSignatureError:
        raise JWTError("Le token a expiré")
    except JWTError as e:
        raise JWTError(f"Token invalide: {e}")


