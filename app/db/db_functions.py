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
    stmt = select(UsersModel).where(UsersModel.id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    return user

async def get_story_by_job_id(job_id: int, db: AsyncSessionLocal):
    from app.models import StoriesModel
    stmt = select(StoriesModel).where(StoriesModel.id == int(job_id))
    result = await db.execute(stmt)
    story = result.scalar_one_or_none()
    return story

async def check_story_ownership(
    user_id: int,
    job_id: int,
    db: AsyncSessionLocal
) -> bool:
    from app.models import StoriesModel
    stmt = select(StoriesModel).where(
        StoriesModel.id == int(job_id),
        StoriesModel.user_id == int(user_id)
    )
    result = await db.execute(stmt)
    story = result.scalar_one_or_none()
    return story is not None

async def get_all_user_stories(user_id: int, session: AsyncSessionLocal):
    from app.models import StoriesModel
    stmt = select(StoriesModel).where(StoriesModel.user_id == int(user_id))
    result = await session.execute(stmt)
    stories = result.scalars().all()
    return stories