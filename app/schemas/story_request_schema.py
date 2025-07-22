from pydantic import BaseModel
from typing import List

class StoryResponseSchema(BaseModel):
    progress: int
    title: str | None
    text: List[str] | None
    images: List[str] | None

class StorySchema(BaseModel):
    title: str | None
    image: str | None

class StoriesResponseSchema(BaseModel):
    stories: List[StorySchema]