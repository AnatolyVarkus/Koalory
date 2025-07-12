from app.db import AsyncSessionLocal
from app.models import UsersModel
from fastapi import HTTPException
from passlib.context import CryptContext
from app.core.config import settings
import datetime
from app.db import get_user_by_email
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTservice:
    def create_access_token(self, user_id: int) -> str:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire
        }
        encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    def create_refresh_token(self, user_id: int) -> str:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire
        }
        encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    # decoding
    def decode_jwt(self, token: str):
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload


async def email_authorize(email: str, password: str):
    async with AsyncSessionLocal() as session:
        user = await get_user_by_email(email, session)

        if user is None or not pwd_context.verify(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user.id


jwt_service = JWTservice()