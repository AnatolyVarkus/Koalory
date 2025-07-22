import aiohttp
from typing import Optional

from fastapi import HTTPException

from app.core.ai_prompts import ai_prompts
from app.models import UsersModel
from app.models.stories import StoriesModel
from app.core import settings, ai_prompts
from app.services.google_storage_service import gcs_uploader
from app.services.ai_photo_analysis import GPTVisionClient
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from app.db import get_story_by_job_id, check_user

class StoryGeneratorService:
    def __init__(self, story: StoriesModel, user: UsersModel):
        self.story = story
        self.user = user

    @classmethod
    async def create(cls, user_id: int, job_id: int):
        async with AsyncSessionLocal() as session:
            story = await get_story_by_job_id(job_id, session)
            user = await check_user(user_id, session)
            return cls(story, user)

    async def build_prompt(self):
        return ai_prompts.get_story_generation_prompt(self.story, self.user.description)

    async def query_claude(self, prompt: str):
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                url="https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1024,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Claude API call failed")
            return await response.json()

    async def run(self):
        prompt = await self.build_prompt()
        return await self.query_claude(prompt)

