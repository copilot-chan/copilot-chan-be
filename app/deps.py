# deps.py
from fastapi import Header
from app.auth import verify_token

def get_current_uid(authorization: str = Header(...)):
    """
    Get token from header and verify, return uid.
    """
    uid = verify_token(authorization)
    return uid
