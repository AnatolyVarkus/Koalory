from app.models import StoriesModel, UsersModel
from app.db import AsyncSessionLocal, db_add, check_user
from app.core import variables
from app.services.ai_photo_generation import AIPhotoGenerator
from app.services.ai_story_generation import StoryGeneratorService
from sqlalchemy import select, and_, func
from fastapi import HTTPException, UploadFile
from typing import Union

class FormHandlerService:
    @staticmethod
    async def handler_create_story(user_id: int):
        async with AsyncSessionLocal() as session:
            print(f"User_id: {user_id}")
            user: UsersModel = await check_user(user_id, session)
            story_count = await session.scalar(select(func.count()).where(StoriesModel.user_id == user.id))
            if user:
                # if (
                #         user.subscription == "free" and story_count >= 1 or
                #         user.subscription == "one" and story_count >= 1 or
                #         user.subscription == "three" and story_count >= 3 or
                #         user.subscription == "ten" and story_count >= 10
                # ):
                #     raise HTTPException(status_code=400, detail=f"Limit exceeded: {story_count}")
                new_story = StoriesModel(user_id=user_id)
                await db_add(new_story, session)
                return new_story.id
            else:
                raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    async def handler_update_first_screen(user_id: int, job_id: int, name: str, gender: str, age: int, location: str, photo):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(StoriesModel).where(and_(StoriesModel.id == job_id,
                                                                           StoriesModel.user_id == user_id)))
            story = result.scalar_one_or_none()
            if story:
                story.story_name = name
                story.story_gender = gender
                story.story_age = age
                story.story_location = location
                await session.commit()
                await session.refresh(story)
                if photo:
                    ai_photo_generator = AIPhotoGenerator()
                    await ai_photo_generator.run(story, photo, job_id, user_id)
                return story.id
            else:
                raise HTTPException(status_code=404, detail="Story not found")

    async def handler_update_story_detail(self, user_id: int, job_id: int, field_name: str, value: Union[int, str]):
        if field_name in variables.ALL_FIELDS:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(StoriesModel).where(and_(StoriesModel.id == job_id, StoriesModel.user_id == int(user_id))))
                story = result.scalar_one_or_none()
                if story:
                    self.update_field(story, field_name, value)
                    await session.commit()
                    if field_name == "message":
                        pass
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
