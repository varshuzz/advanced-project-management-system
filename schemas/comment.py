from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    comment: str = Field(..., min_length=1)


class CommentUpdate(BaseModel):
    comment: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    id: int
    comment: str
    task_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True