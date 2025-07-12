from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")

settings = Settings()
