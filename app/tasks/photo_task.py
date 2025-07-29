from celery import shared_task
from anyio import run as anyio_run
from app.services.ai_photo_generation import AIPhotoGenerator

@shared_task
def run_photo_generation(story, photo, job_id, user_id):
    anyio_run(_run, story, photo, job_id, user_id)

async def _run(story, photo, job_id, user_id):
    ai_photo_generator = AIPhotoGenerator()
    await ai_photo_generator.run(story, photo, job_id, user_id)