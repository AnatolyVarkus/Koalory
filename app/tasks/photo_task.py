from celery import shared_task
from anyio import run as anyio_run
from app.services.ai_photo_generation import AIPhotoGenerator

@shared_task
def run_photo_generation(photo, job_id):
    anyio_run(_run, photo, job_id)

async def _run(photo, job_id):
    ai_photo_generator = AIPhotoGenerator()
    await ai_photo_generator.run(photo, job_id)