from pydantic import BaseModel

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str

class ResetRequest(BaseModel):
    email: str

class ResetVerificationRequest(BaseModel):
    token: str
    password: str


class SuccessfulSubmission(BaseModel):
    success: bool