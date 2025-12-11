# app/schemas/auth.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool = Field(..., alias="is_active")
    designation: Optional[str] = None
    department: Optional[str] = None

    model_config = {
        "from_attributes": True  # Pydantic v2 replacement for orm_mode=True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 42,
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "role": "admin",
                    "is_active": True,
                    "designation": "Manager",
                    "department": "Operations"
                }
            }
        }
