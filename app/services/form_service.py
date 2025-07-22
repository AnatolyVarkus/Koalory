from app.models import StoriesModel
from app.db import AsyncSessionLocal, db_add, check_user
from app.core import variables
from app.services.ai_photo_generation import AIPhotoGenerator
from sqlalchemy import select, and_
from fastapi import HTTPException, UploadFile
from typing import Union

class FormHandlerService:
    @staticmethod
    async def handler_create_story(user_id: int):
        async with AsyncSessionLocal() as session:
            print(f"User_id: {user_id}")
            if await check_user(user_id, session):
                new_story = StoriesModel(user_id=user_id)
                await db_add(new_story, session)
                return new_story.id
            else:
                raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    async def handler_update_first_screen(user_id: int, job_id: int, name: str, gender: str, age: int, location: str, photo: UploadFile):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(StoriesModel).where(and_(StoriesModel.id == job_id,
                                                                           StoriesModel.user_id == user_id)))
            story = result.scalar_one_or_none()
            if story:
                story.name = name
                story.gender = gender
                story.age = age
                story.location = location
                await session.commit()
                if photo:
                    ai_photo_generator = AIPhotoGenerator()
                    photo_bytes = await photo.read()
                    await ai_photo_generator.run(story, photo_bytes, job_id)
                return story.id
            else:
                raise HTTPException(status_code=404, detail="Story not found")

    async def handler_update_story_detail(self, user_id: int, job_id: int, field_name: str, value: Union[int, str]):
        if field_name in variables.ALL_FIELDS:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(StoriesModel).where(and_(StoriesModel.id == job_id, StoriesModel.user_id == user_id)))
                story = result.scalar_one_or_none()
                if story:
                    self.update_field(story, field_name, value)
                    await session.commit()
                    return story.id
                else:
                    raise HTTPException(status_code=404, detail="Story not found")
        else:
            raise HTTPException(status_code=400, detail=f"Incorrect field name, "
                                                        f"use one of these: {variables.ALL_FIELDS}")

    def update_field(self, story: StoriesModel, field_name: str, value: Union[int, str]):
        if not hasattr(story, field_name):
            raise HTTPException(status_code=404, detail=f"Field '{field_name}' does not exist on StoriesModel")
        setattr(story, field_name, value)

form_handler_service = FormHandlerService()
