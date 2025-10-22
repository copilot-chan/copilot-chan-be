import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
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
        return None

    token = authorization.split(" ", 1)[1]

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token.get("uid")
    except auth.InvalidIdTokenError:
        return None
    except auth.ExpiredIdTokenError:
        return None
    except auth.RevokedIdTokenError:
        return None
    except Exception:
        return None
