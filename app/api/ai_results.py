from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.wrapper import CustomRoute
from app.schemas.s2s_schema import SuccessfulResponse
from app.services import jwt_service, form_handler_service, verify_api_token

router = APIRouter(prefix="/ai_results", route_class=CustomRoute)

@router.post("/submit_photo")
async def submit_photo(
        file: UploadFile = File(...),
        token_authorized: bool = Depends(verify_api_token)
) -> SuccessfulResponse:

    if not token_authorized:
        raise HTTPException(status_code=401, detail="Unauthorized")

    contents = await file.read()
    #  s3 или что-то еще сюда

    return SuccessfulResponse(status="ok")


@router.post("/submit_story")
async def submit_story(token_authorized: bool = Depends(verify_api_token)) -> SuccessfulResponse:
    if token_authorized:
        pass

    return SuccessfulResponse(status = "ok")
