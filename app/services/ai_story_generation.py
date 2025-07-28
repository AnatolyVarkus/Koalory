import aiohttp
from typing import Optional

from fastapi import HTTPException
import re
from app.core.ai_prompts import ai_prompts
from app.models import UsersModel
from app.models.stories import StoriesModel
from app.models import PaymentsModel
from typing import Dict, List
from app.core import settings
from app.core.ai_prompts import ai_prompts
from app.services.stripe_service import count_available_stories
from app.services.ai_photo_generation import AIPhotoGenerator
from app.services.google_storage_service import upload_pdf, upload_image
from app.services.ai_photo_analysis import GPTVisionClient
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_, func
from app.db import get_story_by_job_id, check_user, get_all_user_stories
from anthropic import AsyncAnthropic, HUMAN_PROMPT, AI_PROMPT
from anthropic.types import MessageParam, ContentBlockParam, TextBlockParam
from app.services.pdf_service import generate_pdf, test_text
from uuid import uuid4
import asyncio
from time import time
from app.db.db_celery import get_async_sessionmaker



class StoryGeneratorService:
    def __init__(self, job_id: int, user_id: int):
        self.job_id = int(job_id)
        self.user_id = int(user_id)
        print(f"job_id: {self.job_id}, user_id: {self.user_id}")
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def build_prompt(self):
        CeleryAsyncSessionLocal = get_async_sessionmaker()
        async with CeleryAsyncSessionLocal() as session:
            story = await get_story_by_job_id(self.job_id, session)
            user = await check_user(self.user_id, session)
            return ai_prompts.get_story_generation_prompt(story, user.description)

    async def query_claude(self, prompt: str):
        try:
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=8192,
                temperature=0.9,
                system="",
                messages=[
                    MessageParam(
                        role="user",
                        content=[TextBlockParam(type="text", text=prompt)]
                    )
                ]
            )
            print(f"response.content[0].text: {response.content[0].text}")
            return response.content[0].text  # Assuming you want just the text content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")

    import re

    def parse_story_response(self, text: str) -> Dict[str, Optional[str | List[str]]]:
        result: Dict[str, Optional[str | List[str]]] = {
            "title": None,
            "body": None,
            "illustration_prompts": []
        }

        # 1. Вырезаем title
        title_match = re.search(r"\[TITL\]\s*(.*?)\n", text)
        if title_match:
            result["title"] = title_match.group(1).strip()

        # 2. Extract [STRY] ... until [ILLUS]
        body_match = re.search(r"\[STRY\]\s*(.*?)\[ILLUS\]", text, re.DOTALL)
        if body_match:
            result["body"] = body_match.group(1).strip()

        # 3. Extract prompts n1: ... n6:
        prompts = re.findall(r"n\d+:\s*(.*?)(?=\n+n\d+:|$)", text, re.DOTALL)
        result["illustration_prompts"] = [p.strip() for p in prompts]

        print(f"result: {result}")
        return result

    async def update_story(self, title, body, pdf_url, unique):
        CeleryAsyncSessionLocal = get_async_sessionmaker()
        async with CeleryAsyncSessionLocal() as session:
            story: StoriesModel = await get_story_by_job_id(self.job_id, session)
            story.story_title = title
            story.story_text = body
            story.illustration_1 = f"https://storage.googleapis.com/koalory_bucket/photo_1_{unique}.png"
            story.illustration_2 = f"https://storage.googleapis.com/koalory_bucket/photo_2_{unique}.png"
            story.illustration_3 = f"https://storage.googleapis.com/koalory_bucket/photo_3_{unique}.png"
            story.illustration_4 = f"https://storage.googleapis.com/koalory_bucket/photo_4_{unique}.png"
            story.illustration_5 = f"https://storage.googleapis.com/koalory_bucket/photo_5_{unique}.png"
            story.illustration_6 = f"https://storage.googleapis.com/koalory_bucket/photo_6_{unique}.png"
            story.status = "completed"
            story.story_url = pdf_url

            await session.commit()

    async def run(self):
        CeleryAsyncSessionLocal = get_async_sessionmaker()

        async with CeleryAsyncSessionLocal() as session:
            story: StoriesModel = await get_story_by_job_id(self.job_id, session)
            user: UsersModel = await check_user(self.user_id, session)
            stories = await get_all_user_stories(int(self.user_id), session)
            total_stories = len(stories)
            story.status = "started"
            story.story_creation_ts = int(time())
            story.error_message = None

            result = await session.execute(
                select(func.sum(PaymentsModel.available_stories))
                .where(PaymentsModel.user_id == int(self.user_id))
            )
            total_available_stories = result.scalar()
            await session.commit()
            await session.refresh(story)
            if story.story_url is None and total_available_stories >= total_stories:

                prompt = await self.build_prompt()

                tries = 0
                max_tries = 4

                # Step 1: Get Claude response and parse
                for _ in range(max_tries):
                    try:
                        claude_response = await self.query_claude(prompt)
                        result = self.parse_story_response(claude_response)
                        break
                    except Exception:
                        tries += 1
                        if tries >= max_tries:
                            story.status = "error"
                            story.error_message = "We couldn't generate your story, change the details"
                            await session.commit()
                            return None

                # Step 2: Try generating images
                for _ in range(max_tries):
                    try:
                        photo_generator = AIPhotoGenerator()
                        urls = await photo_generator.generate_6_illustrations(result["illustration_prompts"], user.description)
                        unique_story_uuid = str(uuid4())
                        for i, url in enumerate(urls, 1):
                            upload_image(url, f"photo_{i}_{unique_story_uuid}.png")
                        break
                    except Exception:
                        # Retry Claude again in case Leonardo breaks on formatting
                        for _ in range(max_tries):
                            try:
                                claude_response = await self.query_claude(prompt)
                                result = self.parse_story_response(claude_response)
                                break
                            except Exception:
                                continue
                        else:
                            story.status = "error"
                            story.error_message = "We couldn't generate your story, change the details"
                            await session.commit()
                            return None
                else:
                    story.status = "error"
                    story.error_message = "We couldn't generate your story, change the details"
                    await session.commit()
                    return None

                pdf_bytes = generate_pdf(result["title"], result["body"], urls)

                file_name = f"story_{unique_story_uuid}.pdf"

                full_file_name = upload_pdf(file_name, pdf_bytes)
                await self.update_story(result["title"], result["body"], full_file_name, unique_story_uuid)


