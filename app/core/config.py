from pydantic_settings import BaseSettings
from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    DEBUG: bool = False
    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID")
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    API_KEY: str = os.environ.get("API_KEY")
    API_KEY_EXTERNAL: str = os.environ.get("API_KEY_EXTERNAL")

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
    PHOTO_CREATION_TIME_FRAME = 15  # secs
    STORY_CREATION_TIME_FRAME = 300  # secs
    KOALORY_PHOTO_URL = "https://koalory.com/photo"
    KOALORY_STORY_URL = "https://koalory.com/story"

settings = Settings()
variables = Variables()