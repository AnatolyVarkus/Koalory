from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Query
from fastapi.responses import Response
from app.core.wrapper import CustomRoute
from app.schemas.story_request_schema import (StoryResponseSchema, StoriesResponseSchema, StorySchema,
                                              AvailableStoriesSchema)
from app.services import jwt_service, form_handler_service, gcs_uploader
from app.db import AsyncSessionLocal, check_user
from app.models import UsersModel, StoriesModel
from sqlalchemy import select, func
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

auth_scheme = HTTPBearer()

test_link = "https://cdn.leonardo.ai/users/0fad626b-b70d-4f3c-907d-8ee1a30b3e35/generations/d2670342-8852-4fc7-b440-966b00fb6fa7/Leonardo_Phoenix_10_Savva_a_12yearold_boy_from_yale_with_a_Qui_0.jpg"

router = APIRouter(prefix="/story", route_class=CustomRoute)

@router.get("/available_stories")
async def get_available_stories(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> AvailableStoriesSchema:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")

    async with AsyncSessionLocal() as session:
        user: UsersModel = await check_user(user_id, session)
        story_count = await session.scalar(select(func.count()).where(StoriesModel.user_id == user.id))
        if user.subscription == "one":
            return AvailableStoriesSchema(available_stories=1-story_count)
        elif user.subscription == "three":
            return AvailableStoriesSchema(available_stories=3-story_count)
        elif user.subscription == "ten":
            return AvailableStoriesSchema(available_stories=10-story_count)
        else:
            return AvailableStoriesSchema(available_stories=1 - story_count)


@router.get("/request_story")
async def request_story(job_id: int = Query(...), credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> StoryResponseSchema:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")


    return StoryResponseSchema(progress=100, title="Amazing Story", text=["First", "Second"], images=[test_link, test_link])

@router.get("/all_stories")
async def request_story(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> StoriesResponseSchema:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")

    return StoriesResponseSchema(max_stories=3, stories=[StorySchema(title="Once upon a time", image=test_link), StorySchema(title="Oh good time", image=test_link)])

