from pydantic import BaseModel
from typing import Union

class CreateStoryRequest(BaseModel):
    user_id: int

class StoryDetailSubmission(BaseModel):
    job_id: int
    field_name: str
    value: Union[int, str]

class SuccessfulSubmission(BaseModel):
    job_id: int
