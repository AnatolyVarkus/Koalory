from fastapi import APIRouter, HTTPException, Depends
from app.schemas.verification_schema import EmailRequest, EmailVerificationRequest, TokenResponse, SuccessfulSubmission
from app.services import jwt_service
from app.services.verification_service import generate_verification_code, save_verification_code, verify_code
from app.services.email_sender_service import send_email_code  # You must implement this
from app.db import AsyncSessionLocal
from app.models import UsersModel
from app.db import get_user_by_email
from app.core.wrapper import CustomRoute


router = APIRouter(prefix="/verification", route_class=CustomRoute)


@router.post("/create")
async def create_verification(data: EmailRequest) -> SuccessfulSubmission:
    code = generate_verification_code()
    save_verification_code(data.email, code)
    send_email_code(data.email, code)
    return SuccessfulSubmission(success=True)


@router.post("/verify")
async def verify_email(data: EmailVerificationRequest) -> TokenResponse:
    if not verify_code(data.email, data.code):
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    async with AsyncSessionLocal() as session:
        user: UsersModel = await get_user_by_email(data.email, session)
        user.verified = True
        await session.commit()
    access_token = jwt_service.create_access_token(user.id)
    refresh_token = jwt_service.create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)