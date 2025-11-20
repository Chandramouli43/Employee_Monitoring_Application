from pydantic import BaseModel, EmailStr
from typing import Optional

# ---------------------------
# Employee Base Schema
# ---------------------------
class EmployeeBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    role: Optional[str] = "Employee"

# ---------------------------
# Employee Create Schema
# ---------------------------
class EmployeeCreate(EmployeeBase):
    password: str
    contact: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    team_id: Optional[int] = None

# ---------------------------
# Employee Update Schema
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

# ---------------------------
# Employee Response Schema
# ---------------------------
class EmployeeResponse(EmployeeBase):
    id: int
    contact: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    team_id: Optional[int] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True  # ✅ replaces orm_mode in Pydantic v2
