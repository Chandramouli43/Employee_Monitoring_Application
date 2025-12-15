from pydantic import BaseModel
from typing import Optional

# CREATE
class TeamCreate(BaseModel):
    name: str
    department_id: Optional[int] = None

# UPDATE
class TeamUpdate(BaseModel):
    name: Optional[str] = None
    department_id: Optional[int] = None

# RESPONSE
class TeamResponse(BaseModel):
    id: int
    name: str
    department_id: Optional[int]

    class Config:
        from_attributes = True
        validate_by_name = True
