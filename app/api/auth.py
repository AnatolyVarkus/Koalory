from app.core.wrapper import CustomRoute
from fastapi import APIRouter, HTTPException
from app.schemas.register_schema import GoogleRequestSchema, EmailRequestSchema
from app.services import (verify_google_token, email_authorize, jwt_service, RegisterUserService)
from app.db import get_user_by_email, AsyncSessionLocal
from app.schemas.auth_schema import LoginResponse

router = APIRouter(prefix="/auth", route_class=CustomRoute)

@router.post("/google_login")
async def google_login(payload: GoogleRequestSchema) -> LoginResponse:
    id_info = await verify_google_token(payload.email)
    async with AsyncSessionLocal() as session:
        user = await get_user_by_email(id_info["email"], session)
        if not user:
            service = RegisterUserService("google", id_info["email"])
            user_id = await service.register()
        else:
            user_id = user.id
    access_token = jwt_service.create_access_token(user_id)
    refresh_token = jwt_service.create_refresh_token(user_id)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/email_login")
async def email_login(payload: EmailRequestSchema) -> LoginResponse:
    if payload.password is None:
        raise HTTPException(status_code=400, detail="Password is required for email login")
    user_id = await email_authorize(str(payload.email), payload.password)

    access_token = jwt_service.create_access_token(user_id)
    refresh_token = jwt_service.create_refresh_token(user_id)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh")
async def submit_refresh_token(refresh_token: str) -> LoginResponse:
    payload = jwt_service.decode_jwt(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid token type")
    user_id = payload.get("sub")
    new_access = jwt_service.create_access_token(user_id)
    new_refresh = jwt_service.create_refresh_token(user_id)
    return LoginResponse(access_token=new_access, refresh_token=new_refresh)

