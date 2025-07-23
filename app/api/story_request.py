from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Query
from fastapi.responses import Response
from app.core.wrapper import CustomRoute
from app.schemas.story_request_schema import (StoryResponseSchema, StoriesResponseSchema, StorySchema,
                                              AvailableStoriesSchema, SuccessResponseSchema)
from app.services import jwt_service, form_handler_service, StoryGeneratorService
from app.db import AsyncSessionLocal, check_user, get_all_user_stories
from app.models import UsersModel, StoriesModel
from app.core import variables
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from time import time

auth_scheme = HTTPBearer()

test_link = "https://cdn.leonardo.ai/users/0fad626b-b70d-4f3c-907d-8ee1a30b3e35/generations/d2670342-8852-4fc7-b440-966b00fb6fa7/Leonardo_Phoenix_10_Savva_a_12yearold_boy_from_yale_with_a_Qui_0.jpg"

router = APIRouter(prefix="/story", route_class=CustomRoute)

import re

def get_text_before_illustrations(text: str, count: int = 3) -> list[str]:
    parts = re.split(r"\[ILLUSTRATION_\d+]", text)
    return [p.strip() for p in parts[:count] if p != ""]

@router.get("/available_stories")
async def get_available_stories(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> AvailableStoriesSchema:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")

    async with AsyncSessionLocal() as session:
        user: UsersModel = await check_user(user_id, session)
        story_count = await session.scalar(select(func.count()).where(StoriesModel.user_id == int(user.id)))
        if user.subscription == "one":
            available_stories = 1-story_count if 1-story_count >= 0 else 0
        elif user.subscription == "three":
            available_stories = 1 - story_count if 3 - story_count >= 0 else 0
        elif user.subscription == "ten":
            available_stories = 1 - story_count if 10 - story_count >= 0 else 0
        else:
            available_stories = 1 - story_count if 1 - story_count >= 0 else 0

        return AvailableStoriesSchema(available_stories=5)

@router.post("/launch_story_generation")
async def launch_story_generation(job_id: int = Query(...),
                                  credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> SuccessResponseSchema:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")

    story_generator = await StoryGeneratorService.create(user_id, job_id)
    await story_generator.run()

    return SuccessResponseSchema(job_id=job_id)

@router.get("/request_story")
async def request_story(job_id: int = Query(...), credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> StoryResponseSchema:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(StoriesModel).options(selectinload(StoriesModel.user)).where(and_(StoriesModel.id == int(job_id), StoriesModel.user_id == int(user_id))))
        story: StoriesModel = result.scalar_one_or_none()

        if story:
            if story.story_url:
                return StoryResponseSchema(progress=100, title=story.story_title, text=get_text_before_illustrations(story.story_text),
                                           images=[story.illustration_1, story.illustration_2], pdf_url=story.story_url,
                                           email=story.user.email, word_count=len(re.findall(r'\b\w+\b', story.story_text)))
            elif story.story_creation_ts:
                progress = int(((int(time()) - story.story_creation_ts) / variables.STORY_CREATION_TIME_FRAME) * 100)
                return StoryResponseSchema(progress=int(progress) if progress <= 90 else 90)
            else:
                return StoryResponseSchema(progress=0)
        else:
            raise HTTPException(status_code=404, detail="No story found")




def determine_progress(story: StoriesModel) -> str:
    if story.story_creation_ts:
        return "finished"
    elif story.story_name is None or story.photo_url is None:
        return "first_screen"
    elif story.photo_url and story.story_extra is None:
        return "generated_photo"
    elif story.story_extra and story.story_theme is None:
        return "story_theme"
    elif story.story_theme and story.story_message is None:
        return "story_message"
    else:
        return "finished"

@router.get("/all_stories")
async def request_story(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> StoriesResponseSchema:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")

    async with AsyncSessionLocal() as session:
        stories = await get_all_user_stories(user_id, session)
        user = await check_user(user_id, session)
    all_stories = []
    for story in stories:
        all_stories.append(StorySchema(title=story.story_title, image=story.photo_url, job_id=story.id, theme=story.story_theme,
                                       progress=determine_progress(story)))

    if user.subscription == "one":
        max_stories = 1
    elif user.subscription == "three":
        max_stories = 3
    elif user.subscription == "ten":
        max_stories = 10
    else:
        max_stories = 1

    return StoriesResponseSchema(max_stories=max_stories, stories=all_stories)

