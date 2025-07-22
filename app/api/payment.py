from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import Response
from app.core.wrapper import CustomRoute
from app.schemas.payment_schema import (PaymentResponse)
from app.services import jwt_service, form_handler_service, gcs_uploader
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from fastapi.security import OAuth2PasswordBearer
from app.models import StoriesModel
from PIL import Image
from io import BytesIO

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/test_auth")
router = APIRouter(prefix="/payment", route_class=CustomRoute)


@router.post("/generate_payment_link")
async def generate_payment_link(option: str = Form(...), token: str = Depends(oauth2_scheme)) -> PaymentResponse:
    payload = jwt_service.decode_jwt(token)
    user_id = payload.get("sub")

    # Example logic to generate a link
    payment_url = f"https://payment.example.com/checkout?user_id={user_id}&option={option}"
    return PaymentResponse(link=payment_url)