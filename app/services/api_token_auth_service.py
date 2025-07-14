from fastapi import Header, HTTPException
from app.core import settings

async def verify_api_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.removeprefix("Bearer ").strip()

    if token != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API token")

    return True
