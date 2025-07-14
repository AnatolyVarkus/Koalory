from pydantic import BaseModel

class SuccessfulResponse(BaseModel):
    status: str
