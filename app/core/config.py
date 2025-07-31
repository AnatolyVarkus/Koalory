from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()

# Здарова заебал

def str_to_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes")

class Settings(BaseModel):
    DEBUG: bool = False
    LIVE_SERVER: bool = str_to_bool(os.environ.get("LIVE_SERVER"))  # Отличие тестового от live-сервера, для Stripe
    SECRET_KEY: str = os.environ.get("SECRET_KEY")

    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID")
    BUCKET_NAME: str = "koalory_bucket"

    DATABASE_URL: str = os.environ.get("DATABASE_URL")

    LEONARDO_MODEL_ID: str = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"
    LEONARDO_API_KEY: str = os.environ.get("LEONARDO_API_KEY")

    ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY")
    GPT_API_KEY: str = os.environ.get("GPT_API_KEY")

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"  # Redis для Celery
    CELERY_RESULT_BACKEND: str ="redis://localhost:6379/1"  # Redis для Celery

    RESEND_API_KEY: str = os.environ.get("RESEND_API_KEY")  # Email api

    if LIVE_SERVER:
        STRIPE_API_KEY: str = os.environ.get("STRIPE_API_KEY_REAL")
        STRIPE_WEBHOOK_SECRET: str = os.environ.get("STRIPE_WEBHOOK_SECRET_REAL")
    else:
        STRIPE_API_KEY: str = os.environ.get("STRIPE_API_KEY")
        STRIPE_WEBHOOK_SECRET: str = os.environ.get("STRIPE_WEBHOOK_SECRET")



class Variables(BaseModel):
    ALL_FIELDS: list = [
                        "story_extra",
                        "story_theme",
                        "story_message",
                        "story_language"
                        ]
    PHOTO_CREATION_TIME_FRAME: int = 15
    STORY_CREATION_TIME_FRAME: int = 100
    SUBSCRIPTIONS: dict = {
        "one": {"price": 299, "name": "First Story Package"},
        "three": {"price": 599, "name": "Three Stories Package"},
        "ten": {"price": 1499, "name": "Ten Stories Package"}
    }

settings = Settings()
variables = Variables()
