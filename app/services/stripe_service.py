import stripe
from app.core import settings, variables

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
            "user_id": int(user_id)
        },
        success_url=success_url,
        cancel_url="https://story.koalory.com/payment?success=false"
    )
    return session.url
