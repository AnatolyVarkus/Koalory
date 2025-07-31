from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from app.core.wrapper import CustomRoute
from app.schemas.form_schema import (StoryDetailSubmission, SuccessfulSubmission, PhotoLinkResponse)
from app.services import jwt_service, form_handler_service
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from app.models import StoriesModel
from PIL import Image
from io import BytesIO
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

auth_scheme = HTTPBearer()
router = APIRouter(prefix="/form", route_class=CustomRoute)

@router.post("/create_story")
async def create_story(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> SuccessfulSubmission:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")

    job_id = await form_handler_service.handler_create_story(int(user_id))
    return SuccessfulSubmission(job_id=job_id)

@router.post("/submit_first_screen")
async def submit_first_screen(
    job_id: int = Form(...),
    name: str = Form(...),
    gender: str = Form(...),
    age: int = Form(...),
    location: str = Form(...),
    photo: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> SuccessfulSubmission:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")

    job_id = await form_handler_service.handler_update_first_screen(int(user_id), job_id, name, gender, age, location,
                                                                    await normalize_image(photo))
    return SuccessfulSubmission(job_id=job_id)

async def normalize_image(photo: UploadFile) -> bytes:
    image = Image.open(BytesIO(await photo.read()))
    output = BytesIO()
    image.convert("RGB").save(output, format="JPEG")  # or "PNG"
    return output.getvalue()

@router.get("/get_generated_photo")
async def get_generated_photo(
    job_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> PhotoLinkResponse:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(StoriesModel).where(and_(StoriesModel.id == job_id,
                                                                       StoriesModel.user_id == int(user_id))))
        story = result.scalar_one_or_none()
        if not story:
            raise HTTPException(status_code=404, detail=f"Story with id {job_id} not found")
        elif story.photo_status == "error":
            raise HTTPException(status_code=400, detail={"target": "first_screen", "type": "error", "reason": story.photo_error_message})
        elif story.photo_status != "completed":
            raise HTTPException(status_code=400, detail=f"The photo has not been generated yet")
        else:
            return PhotoLinkResponse(photo_link = story.photo_url)

@router.post("/submit_story_detail")
async def submit_story_detail(payload: StoryDetailSubmission,
                              credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> SuccessfulSubmission:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    jwt_payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = jwt_payload.get("sub")
    print(f"user_id: {user_id}")
    job_id = await form_handler_service.handler_update_story_detail(user_id, payload.job_id, payload.field_name, payload.value)
    return SuccessfulSubmission(job_id=job_id)

