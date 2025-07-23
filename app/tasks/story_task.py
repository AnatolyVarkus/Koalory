from celery import shared_task
from app.services.ai_story_generation import StoryGeneratorService
from anyio import run as anyio_run

@shared_task
def run_story_generation(user_id: int, job_id: int):
    anyio_run(_run, user_id, job_id)

async def _run(user_id: int, job_id: int):
    generator = StoryGeneratorService(job_id, user_id)
    await generator.run()