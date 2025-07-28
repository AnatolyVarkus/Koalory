from pydantic import BaseModel, EmailStr

class EmailRequest(BaseModel):
    email: str

class EmailVerificationRequest(BaseModel):
    email: str
    code: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class SuccessfulSubmission(BaseModel):
    success: bool