from pydantic import BaseModel

# ------------------------------
# BASE SCHEMA
# ------------------------------
class DepartmentBase(BaseModel):
    name: str


# ------------------------------
# CREATE SCHEMA
# ------------------------------
class DepartmentCreate(DepartmentBase):
    pass


# ------------------------------
# UPDATE SCHEMA
# ------------------------------
class DepartmentUpdate(BaseModel):
    name: str


# ------------------------------
# RESPONSE SCHEMA
# ------------------------------
class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True
