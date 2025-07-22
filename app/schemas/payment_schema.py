from pydantic import BaseModel

class PaymentResponse(BaseModel):
    link: str

class PaymentRequest(BaseModel):
    option: str
    job_id: int | None = None