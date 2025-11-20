from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.department import DepartmentCreate, DepartmentResponse
from app.models.department import Department
from app.utils.auth import require_roles

router = APIRouter(prefix="/departments", tags=["departments"])

@router.post("/", response_model=DepartmentResponse)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db), _: object = Depends(require_roles("Admin"))):
    existing = db.query(Department).filter(Department.name == dept.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department already exists")
    new = Department(name=dept.name)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get("/", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db), _ = Depends(require_roles("Admin", "Manager", "Employee"))):
    return db.query(Department).all()
