from pydantic import BaseModel
from typing import Optional

# CREATE
class TeamCreate(BaseModel):
    team_name: str
    department_id: Optional[int] = None

# UPDATE
class TeamUpdate(BaseModel):
    team_name: Optional[str] = None
    department_id: Optional[int] = None

# RESPONSE
class TeamResponse(BaseModel):
    id: int
    team_name: str
    department_id: Optional[int]

    class Config:
        from_attributes = True
        validate_by_name = True
