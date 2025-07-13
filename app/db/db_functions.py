from .database import AsyncSessionLocal
from sqlalchemy import select

async def db_add(obj: object, db: AsyncSessionLocal):
    try:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
    except Exception:
        raise

async def get_user_by_email(email: str, db: AsyncSessionLocal):
    from app.models import UsersModel
    stmt = select(UsersModel).where(UsersModel.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user

async def check_user(user_id: int, db: AsyncSessionLocal):
    from app.models import UsersModel
    stmt = select(UsersModel).where(UsersModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user