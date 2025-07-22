from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Query
from fastapi.responses import Response
from app.core.wrapper import CustomRoute
from app.schemas.story_request_schema import (StoryResponseSchema, StoriesResponseSchema, StorySchema)
from app.services import jwt_service, form_handler_service, gcs_uploader
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from fastapi.security import OAuth2PasswordBearer

test_link = "https://cdn.leonardo.ai/users/0fad626b-b70d-4f3c-907d-8ee1a30b3e35/generations/d2670342-8852-4fc7-b440-966b00fb6fa7/Leonardo_Phoenix_10_Savva_a_12yearold_boy_from_yale_with_a_Qui_0.jpg"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/test_auth")
router = APIRouter(prefix="/story", route_class=CustomRoute)


@router.get("/request_story")
async def request_story(job_id: int = Query(...), token: str = Depends(oauth2_scheme)) -> StoryResponseSchema:
    payload = jwt_service.decode_jwt(token)
    user_id = payload.get("sub")


    return StoryResponseSchema(progress=100, title="Amazing Story", text=["First", "Second"], images=[test_link, test_link])

@router.get("/all_stories")
async def request_story(token: str = Depends(oauth2_scheme)) -> StoriesResponseSchema:
    payload = jwt_service.decode_jwt(token)
    user_id = payload.get("sub")

    return StoriesResponseSchema(stories=[StorySchema(title="Once upon a time", image=test_link), StorySchema(title="Oh good time", image=test_link)])

