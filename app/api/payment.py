from fastapi import APIRouter, Depends, Form, File, Request, HTTPException
from fastapi.responses import Response
from app.core.wrapper import CustomRoute
from app.schemas.payment_schema import (PaymentResponse, PaymentRequest)
from app.services import jwt_service, form_handler_service, submit_stripe_payment
from app.db import AsyncSessionLocal
from sqlalchemy import select, and_
from fastapi import Header
from app.core import settings
import stripe

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

@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"].get("user_id")
        bundle = session["metadata"].get("bundle")
        await submit_stripe_payment(user_id, bundle)

    return {"status": "success"}