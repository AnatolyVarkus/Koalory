from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

celery_db_engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
CeleryAsyncSessionLocal = async_sessionmaker(bind=celery_db_engine, expire_on_commit=False)