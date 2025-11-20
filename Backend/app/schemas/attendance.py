from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Attendance schemas
class LoginRequest(BaseModel):
    user_id: str

class LogoutRequest(BaseModel):
    user_id: str

class AttendanceRecord(BaseModel):
    id: str
    user_id: str
    login: datetime
    logout: Optional[datetime]
    worked_hours: Optional[float]

# Leave schemas
class LeaveRequest(BaseModel):
    user_id: str
    start_date: datetime
    end_date: datetime
    reason: str

class LeaveResponse(BaseModel):
    id: str
    user_id: str
    start_date: datetime
    end_date: datetime
    status: str
    reason: str
