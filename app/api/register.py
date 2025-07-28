from fastapi import APIRouter
from app.core.wrapper import CustomRoute
from app.schemas.register_schema import GoogleRequestSchema, EmailRequestSchema
from app.schemas.auth_schema import LoginResponse
from app.services import verify_google_token, RegisterUserService, jwt_service

router = APIRouter(prefix="/register", route_class=CustomRoute)

@router.post("/google_register")
async def google_register_request(payload: GoogleRequestSchema):
    id_info = await verify_google_token(payload.token)
    service = RegisterUserService("google", id_info["email"])
    user_id = await service.register()
    access_token = jwt_service.create_access_token(user_id)
    refresh_token = jwt_service.create_refresh_token(user_id)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/email_register")
async def email_register_request(payload: EmailRequestSchema):
    service = RegisterUserService("email", str(payload.email), payload.password)
    user_id = await service.register()
    access_token = jwt_service.create_access_token(user_id)
    refresh_token = jwt_service.create_refresh_token(user_id)
    return LoginResponse(access_token="", refresh_token="")