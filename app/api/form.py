from fastapi import APIRouter, Depends
from app.core.wrapper import CustomRoute
from app.schemas.form_schema import (StoryDetailSubmission, SuccessfulSubmission)
from app.services import jwt_service, form_handler_service
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(prefix="/form", route_class=CustomRoute)

@router.post("/create_story")
async def create_story(token = Depends(oauth2_scheme)) -> SuccessfulSubmission:
    user_id = jwt_service.decode_jwt(token)
    job_id = await form_handler_service.handler_create_story(user_id)
    return SuccessfulSubmission(job_id=job_id)

@router.post("/submit_story_detail")
async def submit_story_detail(payload: StoryDetailSubmission, token = Depends(oauth2_scheme)) -> SuccessfulSubmission:
    jwt_service.decode_jwt(token)
    job_id = await form_handler_service.handler_update_story_detail(payload.job_id, payload.field_name, payload.value)
    return SuccessfulSubmission(job_id=job_id)