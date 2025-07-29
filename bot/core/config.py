from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseModel):
    TG_TOKEN =  os.getenv("TG_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ALLOWED_USER_IDS = [280963071, 85450372, 322850775, 224737994, 149768]

settings = Settings()
