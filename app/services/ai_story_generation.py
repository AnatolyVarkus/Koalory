import aiohttp
from typing import Optional

from fastapi import HTTPException
import re
from app.core.ai_prompts import ai_prompts
from app.models import UsersModel
from app.models.stories import StoriesModel
from typing import Dict, List
from app.core import settings
from app.core.ai_prompts import ai_prompts
from app.services.ai_photo_generation import AIPhotoGenerator
from app.services.google_storage_service import upload_pdf, upload_image
from app.services.ai_photo_analysis import GPTVisionClient
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from app.db import get_story_by_job_id, check_user
from anthropic import AsyncAnthropic, HUMAN_PROMPT, AI_PROMPT
from anthropic.types import MessageParam, ContentBlockParam, TextBlockParam
from app.services.pdf_service import generate_pdf
from uuid import uuid4
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
        title_match = re.search(r"story_title:\s*(.*?)\n", text)
        if title_match:
            result["title"] = title_match.group(1).strip()

        # 2. Вырезаем тело (от "story:" до "illustration_prompts:")
        body_match = re.search(r"story_body:\s*(.*?)illustration_prompts\s*:", text, re.DOTALL)
        if body_match:
            result["body"] = body_match.group(1).strip()

        # 3. Вырезаем иллюстрации по шаблону n1: [prompt]
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

            story.story_url = pdf_url

            await session.commit()

    async def run(self):
        CeleryAsyncSessionLocal = get_async_sessionmaker()
        async with CeleryAsyncSessionLocal() as session:
            story: StoriesModel = await get_story_by_job_id(self.job_id, session)
            if story.story_url is None:
                prompt = await self.build_prompt()
                claude_response = await self.query_claude(prompt)
                print(f"{claude_response = }")
                result = self.parse_story_response(claude_response)
                photo_generator = AIPhotoGenerator()
                urls = await photo_generator.generate_6_illustrations(result["illustration_prompts"], "")

                unique_story_uuid = str(uuid4())
                upload_image(urls[0], f"photo_1_{unique_story_uuid}.png")
                upload_image(urls[1], f"photo_2_{unique_story_uuid}.png")
                upload_image(urls[2], f"photo_3_{unique_story_uuid}.png")
                upload_image(urls[3], f"photo_4_{unique_story_uuid}.png")
                upload_image(urls[4], f"photo_5_{unique_story_uuid}.png")
                upload_image(urls[5], f"photo_6_{unique_story_uuid}.png")


                pdf_bytes = generate_pdf(result["title"], result["body"], urls)

                file_name = f"story_{unique_story_uuid}.pdf"

                full_file_name = upload_pdf(file_name, pdf_bytes)
                await self.update_story(result["title"], result["body"], full_file_name, unique_story_uuid)
