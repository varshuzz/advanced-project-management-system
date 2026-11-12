from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


#USER REGISTRATION
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: str = "team_member"


#USER LOGIN
class UserLogin(BaseModel):
    email: EmailStr
    password: str


#USER PROFILE UPDATE
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None


#USER PASSWORD CHANGE
class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str

#USER RESPONSE
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        
        