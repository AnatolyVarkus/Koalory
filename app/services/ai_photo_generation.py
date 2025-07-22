import aiohttp
from typing import Optional

from fastapi import HTTPException

from app.core.ai_prompts import ai_prompts
from app.models.stories import StoriesModel
from app.core import settings
from app.services.google_storage_service import gcs_uploader
from app.services.ai_photo_analysis import GPTVisionClient

from app.db import AsyncSessionLocal, check_user
from sqlalchemy import select, and_

class AIPhotoGenerator:
    """
    Handles AI photo generation process:
    1. Analyzes photo with GPT-4V
    2. Builds Leonardo prompt from user info + analysis
    3. Sends request to Leonardo API to generate image
    """

    def __init__(self):
        self.gpt_vision_client = GPTVisionClient()
        self.leonardo_api_key = settings.LEONARDO_API_KEY

    async def analyze_photo(self, story: StoriesModel, photo_bytes: bytes) -> str:
        """Analyze photo with GPT-4V for physical appearance details"""
        prompt = ai_prompts.get_hero_avatar_prompt(story)
        return await self.gpt_vision_client.analyze_image(photo_bytes, prompt)

    async def build_prompt(self, story: StoriesModel, photo_description: str) -> str:
        """Build Leonardo prompt from story + photo analysis"""
        leonardo_prompt = await self.gpt_vision_client.generate_leonardo_prompt(ai_prompts.get_hero_avatar_prompt(story, photo_description))
        return leonardo_prompt

    async def generate_avatar(self, prompt: str) -> Optional[str]:
        """Call Leonardo API to generate image"""
        url = f"https://cloud.leonardo.ai/api/rest/v1/generations"

        headers = {
            "Authorization": f"Bearer {self.leonardo_api_key}",
            "Content-Type": "application/json"
        }

        json_payload = {
            "prompt": prompt,
            "width": 1200,
            "height": 720,
            "modelId": settings.LEONARDO_MODEL_ID, # Replace with actual model ID
            "num_images": 1
        }

        print(f"{prompt = }")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=json_payload) as response:
                if response.status != 200:
                    body = await response.text()
                    raise HTTPException(status_code=400, detail=f"Leonardo API error: {response.status} - {body}")

                data = await response.json()
                try:
                    print(data)
                    return data['sdGenerationJob']["generationId"]  # Adjust according to Leonardo’s response format
                except (KeyError, IndexError) as e:
                    raise HTTPException(status_code=400, detail=f"Leonardo response malformed: {e}")

    async def get_image_from_leonardo(self, image_generation_id: str) -> str:
        url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{image_generation_id}"

        headers = {
            "Authorization": f"Bearer {self.leonardo_api_key}",
            "Content-Type": "application/json"
        }


        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    body = await response.text()
                    raise HTTPException(status_code=400, detail=f"Leonardo API error: {response.status} - {body}")

                data = await response.json()
                try:
                    print(data)
                    return data['generations_by_pk']['generated_images'][0]["url"]  # Adjust according to Leonardo’s response format
                except (KeyError, IndexError):
                    raise HTTPException(status_code=400, detail="Leonardo response malformed")

    async def download_image(self, url: str) -> bytes:
        """Download image from a URL and return its bytes"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail=f"Failed to download image: {response.status}")
                return await response.read()

    async def update_image(self, job_id: int, image_generation_id: str):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(StoriesModel).where(StoriesModel.id == job_id))
            story = result.scalar_one_or_none()
            if not story:
                raise HTTPException(status_code=404, detail=f"Story with id {job_id} not found")

            story.photo_url = f"{image_generation_id}"
            await session.commit()

    async def update_description(self, user_id: int, photo_description: str):
        async with AsyncSessionLocal() as session:
            user = await check_user(user_id, session)
            user.description = photo_description
            await session.commit()

    async def run(self, story: StoriesModel, photo_bytes: bytes, job_id: int, user_id: int):
        """
        Full pipeline: analyze photo, build prompt, generate image
        Returns image URL or raises error
        """
        photo_description = await self.analyze_photo(story, photo_bytes)
        await self.update_description(user_id, photo_description)
        # prompt = await self.build_prompt(story, photo_description)
        image_generation_id = await self.generate_avatar(photo_description)
        await self.update_image(job_id, image_generation_id)

    async def run_secondary(self, image_generation_id: str):
        photo_link = await self.get_image_from_leonardo(image_generation_id)
        photo = await self.download_image(photo_link)
        # gcs_uploader.upload_avatar(image_generation_id, photo)
        return photo_link

# Usage example (you must wire `gpt_vision_client` separately):
# ai_generator = AIPhotoGenerator(gpt_vision_client, settings.LEONARDO_API_KEY)
# image_url = await ai_generator.run(story_model, uploaded_photo.read())