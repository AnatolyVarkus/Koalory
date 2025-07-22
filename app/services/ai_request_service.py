from app.models import StoriesModel
from app.db import AsyncSessionLocal, db_add, check_user, get_story_by_job_id, check_story_ownership
from fastapi import UploadFile
from app.core import settings, variables
from app.schemas.ai_request_schema import PreviewRequestResponse
from sqlalchemy import select
import aiohttp
from fastapi import HTTPException
from time import time
from app.schemas.form_schema import SuccessfulSubmission
from typing import Union

class ExternalRequest:
    @staticmethod
    async def request_photo(user_id: int, job_id: int, photo: UploadFile):
        async with AsyncSessionLocal() as session:
            story: StoriesModel = await get_story_by_job_id(job_id, session)
            if not await check_story_ownership(user_id, job_id, session):
                raise HTTPException(
                    status_code=400,
                    detail="The story doesn't belong to the user"
                )

        if story is None:
            raise HTTPException(status_code=404, detail="No story found")
        elif story.photo_creation_ts is None:
            url = variables.KOALORY_PHOTO_URL
            headers = {
                "Authorization": f"Bearer {settings.API_KEY_EXTERNAL}"
            }

            file_bytes = await photo.read()

            data = aiohttp.FormData()
            data.add_field(
                name="file",
                value=file_bytes,
                filename=photo.filename,
                content_type=photo.content_type
            )
            data.add_field(
                name="job_id",
                value=job_id
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise HTTPException(status_code=response.status, detail=text)


    @staticmethod
    async def request_story(user_id: int, job_id: int):
        async with AsyncSessionLocal() as session:
            story: StoriesModel = await get_story_by_job_id(job_id, session)
            if not await check_story_ownership(user_id, job_id, session):
                raise HTTPException(
                    status_code=400,
                    detail="The story doesn't belong to the user"
                )

        if story is None:
            raise HTTPException(status_code=404, detail="Story not found")
        elif story.story_creation_ts is None:

            url = variables.KOALORY_STORY_URL
            headers = {
                "Authorization": f"Bearer {settings.API_KEY_EXTERNAL}"
            }
            payload = {
                "job_id": job_id,
                "name": story.story_name,
                "age": story.story_age,
                "gender": story.story_gender,
                "location": story.story_location,
                "extra": story.story_extra,
                "theme": story.story_theme,
                "message": story.story_message,
                "language": "en"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise HTTPException(status_code=response.status, detail=text)

class InternalRequest:
    def __init__(self, user_id: int, job_id: int, story: StoriesModel):
        self.user_id = user_id
        self.job_id = job_id
        self.photo_url = story.photo_url
        self.story_url = story.story_url
        self.story_creation_ts = story.story_creation_ts

    @classmethod
    async def create(cls, user_id: int, job_id: int):
        async with AsyncSessionLocal() as session:
            if not await check_story_ownership(user_id, job_id, session):
                raise HTTPException(
                    status_code=400,
                    detail="The story doesn't belong to the user"
                )
            story = await get_story_by_job_id(job_id, session)
            return cls(user_id, job_id, story)

    def request_story(self):
        progress = int(((int(time()) - self.story_creation_ts)/variables.STORY_CREATION_TIME_FRAME) * 100)
        return PreviewRequestResponse(
            url=self.story_url,
            progress= progress if progress <= 100 and self.story_url is None else 100
        )

external_request_handler = ExternalRequest()