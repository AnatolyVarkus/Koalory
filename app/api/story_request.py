from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import Response
from app.core.wrapper import CustomRoute
from app.schemas.story_request_schema import (StoryResponseSchema)
from app.services import jwt_service, form_handler_service, gcs_uploader
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from fastapi.security import OAuth2PasswordBearer
from app.models import StoriesModel
from PIL import Image
from io import BytesIO

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/test_auth")
router = APIRouter(prefix="/story", route_class=CustomRoute)


@router.get("/request_story")
async def request_story(job_id: int = Form(...), token: str = Depends(oauth2_scheme)) -> StoryResponseSchema:
    payload = jwt_service.decode_jwt(token)
    user_id = payload.get("sub")


    return StoryResponseSchema(progress=100, title="Amazing Story", text=["First", "Second"], images=[""])