
from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/anatoly/Important/PycharmProjects/Koalory/app/koalory_google.json"

class Settings(BaseModel):
    DEBUG: bool = False
    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID")
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    API_KEY: str = os.environ.get("API_KEY")
    LEONARDO_MODEL_ID: str = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"
    BUCKET_NAME: str = "koalory_bucket"
    API_KEY_EXTERNAL: str = os.environ.get("API_KEY_EXTERNAL")
    STRIPE_API_KEY: str = os.environ.get("STRIPE_API_KEY")
    LEONARDO_API_KEY: str = os.environ.get("LEONARDO_API_KEY")
    GPT_API_KEY: str = os.environ.get("GPT_API_KEY")



class Variables(BaseModel):
    ALL_FIELDS: list = [
                        "story_name",
                        "story_age",
                        "story_gender",
                        "story_location",
                        "story_extra",
                        "story_theme",
                        "story_message"
                        ]
    PHOTO_CREATION_TIME_FRAME: int = 15  # secs
    STORY_CREATION_TIME_FRAME: int = 300  # secs
    KOALORY_PHOTO_URL: str = "https://koalory.com/photo"
    KOALORY_STORY_URL: str = "https://koalory.com/story"

settings = Settings()
variables = Variables()
