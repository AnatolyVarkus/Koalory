from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException
from app.core.config import settings

async def verify_google_token(token: str) -> dict:
    try:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        return id_info

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {e}")
