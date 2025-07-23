import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import settings, variables
from app.db import AsyncSessionLocal, db_add, get_all_user_stories
from app.models import PaymentsModel
from sqlalchemy import select, func
stripe.api_key = settings.STRIPE_API_KEY

def create_stripe_payment_link(user_id: int, job_id: int | None, option: str) -> str:
    if job_id is None:
        success_url = f"https://story.koalory.com/payment?success=true"
    else:
        success_url = f"https://story.koalory.com/payment?success=true&job_id={job_id}"
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": variables.SUBSCRIPTIONS[option]["price"],
                    "product_data": {
                        "name": variables.SUBSCRIPTIONS[option]["name"],
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={
            "user_id": int(user_id),
            "bundle": str(option)
        },
        success_url=success_url,
        cancel_url="https://story.koalory.com/payment?success=false"
    )
    return session.url

async def submit_stripe_payment(
    user_id: int,
    option: str,
):
    async with AsyncSessionLocal() as session:
        if option == "one":
            available_stories = 1
        elif option == "three":
            available_stories = 3
        elif option == "ten":
            available_stories = 10
        new_payment = PaymentsModel(user_id = user_id, bundle_name=option, available_stories=available_stories)
        await db_add(new_payment, session)

async def count_available_stories(user_id: int):
    async with AsyncSessionLocal() as session:
        stories = await get_all_user_stories(user_id, session)
        total_stories = len(stories)

        result = await session.execute(
            select(func.sum(PaymentsModel.available_stories))
            .where(PaymentsModel.user_id == user_id)
        )
        total = result.scalar()
        return total or 0, total_stories