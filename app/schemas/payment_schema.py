from pydantic import BaseModel

class PaymentResponse(BaseModel):
    link: str
