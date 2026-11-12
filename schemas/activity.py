from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ActivityResponse(BaseModel):
    id: int
    action: str
    details: Optional[str] = None
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
        
        