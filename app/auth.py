import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-key.json")

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

def verify_token(authorization: str | None) -> str | None:
    """
    Verifies the Firebase ID token from the Authorization header string.

    Args:
        authorization: The full "Authorization" header value (e.g., "Bearer <token>"). 

    Returns:
        The user ID (uid) if the token is valid, otherwise None.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or malformed")

    token = authorization.split(" ", 1)[1]

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token.get("uid")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token expired")
    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=401, detail="Token revoked")
    except Exception:
        raise HTTPException(status_code=401, detail="Unknown token error")
