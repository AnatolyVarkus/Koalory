from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import Response
from app.core.wrapper import CustomRoute
from app.schemas.payment_schema import (PaymentResponse, PaymentRequest)
from app.services import jwt_service, form_handler_service
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from fastapi import Header

from fastapi.security import OAuth2PasswordBearer
from app.models import StoriesModel
from PIL import Image
from io import BytesIO
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services import create_stripe_payment_link

auth_scheme = HTTPBearer()
router = APIRouter(prefix="/payment", route_class=CustomRoute)


@router.post("/generate_payment_link")
async def generate_payment_link(payload: PaymentRequest,
                                credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> PaymentResponse:
    print(f"{payload.option = }")
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    jwt_payload = jwt_service.decode_jwt(credentials.credentials)
    user_id = jwt_payload.get("sub")

    link = create_stripe_payment_link(user_id, payload.job_id, payload.option)
    return PaymentResponse(link=link)
