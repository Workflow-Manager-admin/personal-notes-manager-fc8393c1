from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=64, description="Username (unique)")
    email: EmailStr
    password: str = Field(..., min_length=5)

# PUBLIC_INTERFACE
class UserResponse(BaseModel):
    """User info schema returned by API."""
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT access token response."""
    access_token: str
    token_type: str

# PUBLIC_INTERFACE
class TokenData(BaseModel):
    """Token payload contents."""
    user_id: Optional[int] = None

# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Base note fields."""
    title: str = Field(..., max_length=255)
    content: Optional[str] = Field(None, max_length=4000)

# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Fields to create note."""

# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Fields to update note."""
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, max_length=4000)

# PUBLIC_INTERFACE
class NoteResponse(NoteBase):
    """Note item returned by API."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    owner_id: int

    class Config:
        orm_mode = True
