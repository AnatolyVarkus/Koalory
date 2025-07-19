import stripe
from app.core import settings

stripe.api_key = settings.STRIPE_API_KEY

def create_stripe_payment_link(amount_cents: int, product_name: str) -> str:
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": amount_cents,
                    "product_data": {
                        "name": product_name,
                    },
                },
                "quantity": 1,
            },
        ],
        success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://yourdomain.com/cancel",
    )
    return session.url
