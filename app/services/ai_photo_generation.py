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

    async def analyze_photo(self, photo_bytes: bytes) -> str:
        """Analyze photo with GPT-4V for physical appearance details"""
        prompt = ai_prompts.get_photo_analysis_prompt()
        return await self.gpt_vision_client.analyze_image(photo_bytes, prompt)

    def build_prompt(self, story: StoriesModel, photo_description: str) -> str:
        """Build Leonardo prompt from story + photo analysis"""
        return ai_prompts.get_hero_avatar_prompt(story, photo_description)

    async def generate_avatar(self, prompt: str) -> Optional[str]:
        """Call Leonardo API to generate image"""
        url = f"https://cloud.leonardo.ai/api/rest/v1/generations"

        headers = {
            "Authorization": f"Bearer {self.leonardo_api_key}",
            "Content-Type": "application/json"
        }

        json_payload = {
            "prompt": prompt,
            "num_images": 1,
            "width": 1024,
            "height": 1024,
            "modelId": settings.LEONARDO_MODEL_ID # Replace with actual model ID
        }

        print(f"{prompt = }")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=json_payload) as response:
                if response.status != 200:
                    body = await response.text()
                    raise HTTPException(status_code=400, detail=f"Leonardo API error: {response.status} - {body}")

                data = await response.json()
                try:
                    return data['generations'][0]['image']  # Adjust according to Leonardo’s response format
                except (KeyError, IndexError):
                    raise HTTPException(status_code=400, detail="Leonardo response malformed")

    async def download_image(self, url: str) -> bytes:
        """Download image from a URL and return its bytes"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail=f"Failed to download image: {response.status}")
                return await response.read()

    async def update_image(self, job_id: int):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(StoriesModel).where(StoriesModel.id == job_id))
            story = result.scalar_one_or_none()
            if not story:
                raise HTTPException(status_code=404, detail=f"Story with id {job_id} not found")

            story.photo_url = f"{job_id}_avatar_image.png"
            await session.commit()

    async def run(self, story: StoriesModel, photo_bytes: bytes, job_id: int):
        """
        Full pipeline: analyze photo, build prompt, generate image
        Returns image URL or raises error
        """
        photo_description = await self.analyze_photo(photo_bytes)
        prompt = self.build_prompt(story, photo_description)
        image_url = await self.generate_avatar(prompt)
        photo = await self.download_image(image_url)
        gcs_uploader.upload_avatar(job_id, photo)

# Usage example (you must wire `gpt_vision_client` separately):
# ai_generator = AIPhotoGenerator(gpt_vision_client, settings.LEONARDO_API_KEY)
# image_url = await ai_generator.run(story_model, uploaded_photo.read())