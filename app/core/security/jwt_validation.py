from fastapi import Request, HTTPException
from jose import jwt

def validate_jwt(token: str):
    try:
        payload = jwt.get_unverified_claims(token)
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")