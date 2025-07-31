from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

def get_async_sessionmaker():
    celery_db_engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
    return async_sessionmaker(bind=celery_db_engine, expire_on_commit=False)