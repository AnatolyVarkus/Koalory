from celery import Celery
from app.core import settings
from app.tasks import story_task, photo_task

celery = Celery(
    'worker',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.autodiscover_tasks(['app.tasks'])