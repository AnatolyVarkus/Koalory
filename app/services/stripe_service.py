import stripe
from app.core import settings, variables

stripe.api_key = settings.STRIPE_API_KEY

def create_stripe_payment_link(user_id: int, job_id: int, option: str) -> str:
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
            "user_id": int(user_id)
        },
        success_url=f"https://story.koalory.com/success?job_id={job_id}",
        cancel_url="https://yourdomain.com/cancel"
    )
    return session.url
