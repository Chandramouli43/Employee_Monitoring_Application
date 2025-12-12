from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    department: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    productivity_score: Optional[float] = 0.0
    tasks_completed: Optional[int] = 0
    hours_logged: Optional[float] = 0.0

class EmployeeUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    department: Optional[str]
    productivity_score: Optional[float]
    tasks_completed: Optional[int]
    hours_logged: Optional[float]
    is_active: Optional[bool]

class EmployeeResponse(EmployeeBase):
    id: int
    productivity_score: float
    tasks_completed: int
    hours_logged: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

class EmployeeRead(EmployeeBase):
    id: int
    is_active: bool
    created_at: datetime    

    class Config:
        from_attributes = True

class ProductivityBase(BaseModel):
    employee_id: int
    period: Optional[str] = None           
    average_score: Optional[float] = 0.0
    tasks_completed: Optional[int] = 0
    hours_logged: Optional[float] = 0.0
    score: Optional[float] = None          
    timestamp: Optional[datetime] = None   

class ProductivityCreate(ProductivityBase):
    pass

class ProductivityResponse(ProductivityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SummaryMetrics(BaseModel):
    overall_score: float
    average_hours: float
    tasks_completed: int
