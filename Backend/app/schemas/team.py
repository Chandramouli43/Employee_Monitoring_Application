from pydantic import BaseModel
from typing import Optional

class TeamCreate(BaseModel):
    name: str
    department_id: Optional[int] = None

class TeamResponse(BaseModel):
    id: int
    name: str
    department_id: Optional[int]

    class Config:
        from_attributes = True
        validate_by_name = True  
