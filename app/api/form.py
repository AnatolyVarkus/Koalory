from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import Response
from app.core.wrapper import CustomRoute
from app.schemas.form_schema import (StoryDetailSubmission, SuccessfulSubmission, FirstScreenSubmission)
from app.services import jwt_service, form_handler_service, gcs_uploader
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from fastapi.security import OAuth2PasswordBearer
from app.models import StoriesModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/test_auth")
router = APIRouter(prefix="/form", route_class=CustomRoute)

@router.post("/create_story")
async def create_story(token: str = Depends(oauth2_scheme)) -> SuccessfulSubmission:
    # payload = jwt_service.decode_jwt(token)
    # user_id = payload.get("sub")

    job_id = await form_handler_service.handler_create_story(1)
    return SuccessfulSubmission(job_id=job_id)

@router.post("/submit_first_screen")
async def submit_first_screen(
    job_id: int = Form(...),
    name: str = Form(...),
    gender: str = Form(...),
    age: int = Form(...),
    location: str = Form(...),
    photo: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
) -> SuccessfulSubmission:
    # payload = jwt_service.decode_jwt(token)
    # user_id = payload.get("sub")

    job_id = await form_handler_service.handler_update_first_screen(1, job_id, name, gender, age, location, photo)
    return SuccessfulSubmission(job_id=job_id)

@router.get("/get_generated_photo")
async def get_generated_photo(
    job_id: int,
    token: str = Depends(oauth2_scheme)
) -> Response:
    # payload = jwt_service.decode_jwt(token)
    # user_id = payload.get("sub")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(StoriesModel).where(and_(StoriesModel.id == job_id,
                                                                       StoriesModel.user_id == 1)))
        story = result.scalar_one_or_none()
        if not story:
            raise HTTPException(status_code=404, detail=f"Story with id {job_id} not found")
        if story.photo_url is None:
            raise HTTPException(status_code=400, detail=f"The photo has not been generated yet")
    image_bytes = gcs_uploader.get_avatar_bytes(job_id)
    return Response(content=image_bytes, media_type="image/png")

@router.post("/submit_story_detail")
async def submit_story_detail(payload: StoryDetailSubmission, token: str = Depends(oauth2_scheme)) -> SuccessfulSubmission:
    jwt_service.decode_jwt(token)
    job_id = await form_handler_service.handler_update_story_detail(payload.job_id, payload.field_name, payload.value)
    return SuccessfulSubmission(job_id=job_id)