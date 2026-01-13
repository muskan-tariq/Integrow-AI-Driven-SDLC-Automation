from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    github_username: str = Field(..., min_length=1, max_length=39)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    github_id: str = Field(..., min_length=1)
    access_token_encrypted: str = Field(..., min_length=1)

class UserUpdate(BaseModel):
    github_username: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    access_token_encrypted: Optional[str] = None

class UserResponse(UserBase):
    id: str
    github_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: str
    github_username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    github_id: str
    created_at: datetime

    class Config:
        from_attributes = True