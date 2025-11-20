from pydantic import BaseModel, EmailStr
from typing import Optional


# ---------------------------
# Base Schema (shared fields)
# ---------------------------
class EmployeeBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    role: Optional[str] = "Employee"
    contact: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None  # nullable foreign key
    team_id: Optional[int] = None         # nullable foreign key


# ---------------------------
# Create Schema (for POST)
# ---------------------------
class EmployeeCreate(EmployeeBase):
    password: str


# ---------------------------
# Update Schema (for PUT/PATCH)
# ---------------------------
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


# ---------------------------
# Response Schema (for GET)
# ---------------------------
class EmployeeResponse(EmployeeBase):
    id: int
    is_active: bool
    productivity_score: float
    tasks_completed: int
    hours_logged: float

    class Config:
        from_attributes = True  # ✅ replaces orm_mode
        validate_by_name = True
