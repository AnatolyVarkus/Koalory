from fastapi import HTTPException
from passlib.context import CryptContext
from app.models import UsersModel
from app.db import db_add, get_user_by_email, AsyncSessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterUserService:
    def __init__(self, method: str, email: str, password: str | None = None):
        self.method = method
        self.email = email
        self.password = password
        self.hashed_password = self.hash_password()

    async def register(self):
        async with AsyncSessionLocal() as session:
            user = await get_user_by_email(self.email, session)
            if user:
                if self.method == "google":
                    return user.id
                raise HTTPException(status_code=400, detail="User already exists")

            new_user = UsersModel(email=self.email, method=self.method, hashed_password=self.hashed_password)
            await db_add(new_user, session)
            return new_user.id

    def hash_password(self) -> str | None:
        return None if self.password is None else str(pwd_context.hash(str(self.password)))

