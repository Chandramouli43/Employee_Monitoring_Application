from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, date


class AttendanceOut(BaseModel):
    id: int
    date: date
    login_time: datetime | None
    logout_time: datetime | None
    total_hours: str
    status: str

    class Config:
        from_attributes = True



class LeaveOut(BaseModel):
    id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str
    applied_on: datetime

    class Config:
        from_attributes = True



class ActivityOut(BaseModel):
    id: int
    description: str
    timestamp: datetime

    class Config:
        from_attributes = True



class ProductivityOut(BaseModel):
    id: int
    score: float
    date: date

    class Config:
        from_attributes = True



class EmployeeCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    password: str
    role: Optional[str] = "Employee"
    contact: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    team_id: Optional[int] = None



class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    contact: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    team_id: Optional[int] = None
    is_active: Optional[bool] = None



class EmployeeResponse(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    email: EmailStr
    role: str
    contact: Optional[str]
    designation: Optional[str]
    department_name: Optional[str]
    department_id: Optional[int]
    team_name:Optional[str]
    team_id: Optional[int]
    is_active: bool

    attendances: List[AttendanceOut] = []
    leaves: List[LeaveOut] = []
    activities: List[ActivityOut] = []
    productivity: List[ProductivityOut] = []
    screenshots: list = []
    alerts: list = []

    productivity_score: float = 0
    tasks_completed: int = 0
    hours_logged: float = 0

    class Config:
        from_attributes = True


from pydantic import BaseModel, EmailStr
from typing import Optional

class EmployeeListResponse(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    email: EmailStr
    role: str

    contact: Optional[str]
    designation: Optional[str]

    department_id: Optional[int]
    department_name: Optional[str]

    team_id: Optional[int]
    team_name: Optional[str]

    is_active: bool

    productivity_score: float = 0
    tasks_completed: int = 0
    hours_logged: float = 0

    class Config:
        from_attributes = True
