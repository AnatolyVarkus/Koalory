from pydantic import BaseModel
from typing import List

class StoryResponseSchema(BaseModel):
    progress: int
    title: str | None = None
    text: List[str] | None = None
    images: List[str] | None = None
    pdf_url: str | None = None
    email: str | None = None
    word_count: int | None = None

class StorySchema(BaseModel):
    title: str | None = None
    image: str | None = None
    job_id: int | None = None
    theme: str | None = None
    progress: str | None = None

class StoriesResponseSchema(BaseModel):
    max_stories: int
    stories: List[StorySchema]

class AvailableStoriesSchema(BaseModel):
    available_stories: int

class SuccessResponseSchema(BaseModel):
    job_id: int

