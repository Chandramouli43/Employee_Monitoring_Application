from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------------------------
# Base schema for Activity
# ---------------------------
class ActivityBase(BaseModel):
    employee_id: Optional[int] = None  # Optional if set automatically
    department_id: Optional[int] = None
    team_id: Optional[int] = None
    activity_type: str  # e.g., "app", "website", "idle"
    name: Optional[str] = None         # App name or website
    description: Optional[str] = None  # Extra info
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    activity_metadata: Optional[str] = None  
    timestamp: Optional[datetime] = None     
    productive: Optional[str] = None         

# ---------------------------
# Schema for creating an Activity
# ---------------------------
class ActivityCreate(ActivityBase):
    pass

# ---------------------------
# Schema for reading Activity from DB
# ---------------------------
class ActivityResponse(ActivityBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        # ✅ Pydantic v2 syntax
        from_attributes = True  # replaces orm_mode=True
