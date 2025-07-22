from pydantic import BaseModel
from typing import Union

class CreateStoryRequest(BaseModel):
    user_id: int

class StoryDetailSubmission(BaseModel):
    job_id: int
    field_name: str
    value: Union[int, str]

class FirstScreenSubmission(BaseModel):
    job_id: int
    name: str
    age: int
    location: str

class SuccessfulSubmission(BaseModel):
    job_id: int

class PhotoLinkResponse(BaseModel):
    photo_link: str