from pydantic import BaseModel, EmailStr

class GoogleRequestSchema(BaseModel):
    token: str

class EmailRequestSchema(BaseModel):
    email: EmailStr
    password: str
