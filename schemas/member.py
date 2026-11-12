from pydantic import BaseModel, Field
from datetime import datetime


class MemberCreate(BaseModel):
    user_id: int
    role: str = Field(default="team_member")


class MemberUpdate(BaseModel):
    role: str


class MemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True
        
        