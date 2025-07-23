from celery import shared_task
from app.services.ai_story_generation import StoryGeneratorService
import asyncio

@shared_task
def run_story_generation(user_id: int, job_id: int):
    asyncio.run(_run(user_id, job_id))

async def _run(user_id: int, job_id: int):
    generator = StoryGeneratorService(job_id, user_id)
    await generator.run()