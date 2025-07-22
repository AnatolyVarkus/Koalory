from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import Response
from app.core.wrapper import CustomRoute
from app.schemas.payment_schema import (PaymentResponse)
from app.services import jwt_service, form_handler_service, gcs_uploader
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from fastapi import Header

from fastapi.security import OAuth2PasswordBearer
from app.models import StoriesModel
from PIL import Image
from io import BytesIO
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

auth_scheme = HTTPBearer()
router = APIRouter(prefix="/payment", route_class=CustomRoute)


@router.post("/generate_payment_link")
async def generate_payment_link(option: str = Form(...), credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> PaymentResponse:
    print(f"{option = }")
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = payload.get("sub")


    payment_url = f"https://payment.example.com/checkout?user_id={user_id}&option={option}"
    return PaymentResponse(link=payment_url)
