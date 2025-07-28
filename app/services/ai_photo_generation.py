import aiohttp
from typing import Optional

from fastapi import HTTPException

from app.core.ai_prompts import ai_prompts
from app.models.stories import StoriesModel
from app.core import settings
import asyncio
from app.services.google_storage_service import upload_avatar
from app.services.ai_photo_analysis import GPTVisionClient
import asyncio
from app.db import AsyncSessionLocal, get_story_by_job_id
from sqlalchemy import select, and_
import requests
from uuid import uuid4

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
                    img_url = data['generations_by_pk']['generated_images'][0]["url"]
                except (KeyError, IndexError):
                    raise HTTPException(status_code=400, detail="Leonardo response malformed")

        # Now test the URL with retries
        for attempt in range(5):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(img_url, timeout=10) as img_response:
                        if img_response.status == 200:
                            return img_url
            except Exception as e:
                print(f"[Leonardo CDN Retry] Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 * (attempt + 1))

        raise HTTPException(status_code=500, detail="Leonardo CDN returned invalid image repeatedly.")

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

    async def update_description(self, job_id: int, photo_description: str):
        async with AsyncSessionLocal() as session:
            story = await get_story_by_job_id(job_id, session)
            story.user_description = photo_description
            await session.commit()


    async def run(self, story: StoriesModel, photo_bytes: bytes, job_id: int, user_id: int):
        """
        Full pipeline: analyze photo, build prompt, generate image
        Returns image URL or raises error
        """
        photo_description = await self.analyze_photo(story, photo_bytes)
        await self.update_description(job_id, photo_description)
        # prompt = await self.build_prompt(story, photo_description)
        image_generation_id = await self.generate_avatar(photo_description)
        tries = 0
        try:
            while tries < 6:
                await asyncio.sleep(2)
                try:
                    link = await self.run_secondary(image_generation_id, job_id)
                    if link:
                        break
                except:
                    pass

                tries += 1
        except Exception as e:
            return HTTPException(status_code=400, detail={"type": "error", "target": "first_screen", "reason": e})






    async def run_secondary(self, image_generation_id: str, job_id: int):
        photo_link = await self.get_image_from_leonardo(image_generation_id)
        unique_address = f"avatar_{str(uuid4())}.png"
        full_photo_link = upload_avatar(photo_link, unique_address)
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(StoriesModel).where(StoriesModel.id == job_id))
            story = result.scalar_one_or_none()

            story.photo_url = full_photo_link
            await session.commit()
        return full_photo_link



    async def generate_6_illustrations(self, prompts, character_description):
        print(f"PROMPTS = {prompts}")
        generated_images = []
        for prompt in prompts:
            image = await self.generate_avatar(prompt+f"\n Extra character description: \n {character_description}")
            tries = 0
            while tries < 6:
                try:
                    url = await self.get_image_from_leonardo(image)
                    generated_images.append(await fetch_image_bytes(url))
                    break
                except Exception as e:
                    tries += 1
                    await asyncio.sleep(4 * tries)
        return generated_images

async def fetch_image_bytes(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch image: {response.status}")
            return await response.read()

# Usage example (you must wire `gpt_vision_client` separately):
# ai_generator = AIPhotoGenerator(gpt_vision_client, settings.LEONARDO_API_KEY)
# image_url = await ai_generator.run(story_model, uploaded_photo.read())