from celery import Celery
from app.core import settings  # assuming you have Redis/host info in your settings
from app.tasks import story_task  # force-load the module

celery = Celery(
    'worker',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.autodiscover_tasks(['app.tasks'])  # Make sure your tasks package is here