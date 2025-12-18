from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)
from app.models.department import Department
from app.utils.auth import require_roles

router = APIRouter(prefix="/departments", tags=["Departments"])
 

# -----------------------------------------
# CREATE DEPARTMENT (Admin only)
# -----------------------------------------
@router.post("/", response_model=DepartmentResponse)
def create_department(
    dept: DepartmentCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    existing = (
        db.query(Department)
        .filter(Department.name == dept.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Department already exists")

    new_dept = Department(name=dept.name)
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept

# LIST DEPARTMENTS

@router.get("/", response_model=list[DepartmentResponse])
def list_departments(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin", "Manager", "Employee")),
):
    return db.query(Department).all()

# UPDATE DEPARTMENT

@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    dept: DepartmentUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    existing = db.query(Department).filter(Department.id == dept_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Department not found")

    existing.name = dept.name

    db.commit()
    db.refresh(existing)
    return existing

# DELETE DEPARTMENT

@router.delete("/{dept_id}")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    db.delete(dept)
    db.commit()
    return {"message": "Department deleted successfully"}
