from app.models import StoriesModel
from app.db import AsyncSessionLocal, db_add, check_user
from app.core import variables
from sqlalchemy import select
from fastapi import HTTPException
from typing import Union

class FormHandlerService:
    async def handler_create_story(self, user_id: int):
        async with AsyncSessionLocal() as session:
            if await check_user(user_id, session):
                new_story = StoriesModel(user_id=user_id)
                await db_add(new_story, session)
                return new_story.id
            else:
                raise HTTPException(status_code=404, detail="User not found")

    async def handler_update_story_detail(self, job_id: int, field_name: str, value: Union[int, str]):
        if field_name in variables.ALL_FIELDS:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(StoriesModel).where(StoriesModel.id == job_id))
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
            raise ValueError(f"Field '{field_name}' does not exist on StoriesModel")
        setattr(story, field_name, value)

form_handler_service = FormHandlerService()
