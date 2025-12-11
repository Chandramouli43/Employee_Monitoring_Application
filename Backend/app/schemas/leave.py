from pydantic import BaseModel
from datetime import date
from typing import Optional
 
 
class LeaveRequest(BaseModel):
    start_date: date
    end_date: date
    reason: str
 
 
class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    status: str
    reason: str
 
    class Config:
        from_attributes = True