from pydantic import BaseModel

class RequestStoryCreation(BaseModel):
    job_id: int

class PreviewRequestResponse(BaseModel):
    url: str
    progress: int