from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.wrapper import CustomRoute
from app.schemas.s2s_schema import SuccessfulResponse
from app.schemas.ai_request_schema import PreviewRequestResponse, RequestStoryCreation
from app.services import jwt_service, form_handler_service, verify_api_token, external_request_handler, InternalRequest
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


router = APIRouter(prefix="/ai_requests", route_class=CustomRoute)

@router.post("/request_photo")
async def request_photo(
        payload: RequestStoryCreation,
        file: UploadFile = File(...),
        token: bool = Depends(oauth2_scheme)
) -> SuccessfulResponse:
    user_id = jwt_service.decode_jwt(token)

    await external_request_handler.request_photo(user_id, payload.job_id, file)
    return SuccessfulResponse(status="ok")

@router.post("/request_story")
async def request_story(
        payload: RequestStoryCreation,
        token: bool = Depends(oauth2_scheme)
) -> SuccessfulResponse:
    user_id = jwt_service.decode_jwt(token)

    await external_request_handler.request_story(user_id, payload.job_id)
    return SuccessfulResponse(status="ok")

@router.post("/check_photo")
async def check_photo(
        payload: RequestStoryCreation,
        token: bool = Depends(oauth2_scheme)
) -> PreviewRequestResponse:

    user_id = jwt_service.decode_jwt(token)

    handler = await InternalRequest.create(user_id=user_id, job_id=payload.job_id)
    return handler.request_photo()

@router.post("/check_story")
async def check_story(
        payload: RequestStoryCreation,
        token: bool = Depends(oauth2_scheme)
) -> PreviewRequestResponse:
    user_id = jwt_service.decode_jwt(token)

    handler = await InternalRequest.create(user_id=user_id, job_id=payload.job_id)
    return handler.request_story()