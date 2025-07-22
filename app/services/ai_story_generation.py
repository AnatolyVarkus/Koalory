import aiohttp
from typing import Optional

from fastapi import HTTPException

from app.core.ai_prompts import ai_prompts
from app.models.stories import StoriesModel
from app.core import settings
from app.services.google_storage_service import gcs_uploader
from app.services.ai_photo_analysis import GPTVisionClient
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from app.db import get_story_by_job_id

class StoryGeneratorService:
    def __init__(self, story: StoriesModel):
        self.story = story

    @classmethod
    async def create(cls, user_id: int, job_id: int):
        async with AsyncSessionLocal() as session:
            story = await get_story_by_job_id(job_id, session)
            return cls(story)



    async def run(self):
        pass
