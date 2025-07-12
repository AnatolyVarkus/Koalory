from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    DEBUG: bool = False
    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID")
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")

settings = Settings()
