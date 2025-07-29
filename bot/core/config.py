from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
import os
load_dotenv()

class Settings(BaseModel):
    TG_TOKEN: str =  os.getenv("TG_TOKEN")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ALLOWED_USER_IDS: List = [280963071, 85450372, 322850775, 224737994, 149768]

settings = Settings()
