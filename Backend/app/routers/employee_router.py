from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session, selectinload
from pathlib import Path
from typing import Optional, List
import shutil

from app.core.database import get_db
from app.core.config import UPLOAD_DIR
from app.schemas.employee_schema import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import (
    create_employee,
    get_employee_by_email,
    get_employee_by_id,
    update_profile,
)
from app.utils.auth import require_roles, get_current_user
from app.models.employee import Employee

router = APIRouter(prefix="/employees", tags=["employees"])


# ====================================================
# Helper function to inject required fields
# ====================================================
def attach_extra_fields(emp: Employee):
    emp.department_name = emp.department.name if emp.department else None
    emp.team_name = emp.team.name if emp.team else None
    return emp


# ====================================================
# Create new employee
# ====================================================
@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def register_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    existing = get_employee_by_email(db, employee.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    emp = create_employee(db, employee)
    return attach_extra_fields(emp)


# ====================================================
# Get own profile
# ====================================================
@router.get("/me", response_model=EmployeeResponse)
def read_own_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = (
        db.query(Employee)
        .options(
            selectinload(Employee.attendances),
            selectinload(Employee.leaves),
            selectinload(Employee.activities),
            selectinload(Employee.productivity),
            selectinload(Employee.screenshots),
            selectinload(Employee.alerts),
            selectinload(Employee.department),
            selectinload(Employee.team),
        )
        .filter(Employee.id == current_user.id)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return attach_extra_fields(user)


# ====================================================
# List all employees
# ====================================================
@router.get("/", response_model=List[EmployeeResponse])
def list_all_employees(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    employees = (
        db.query(Employee)
        .options(
            selectinload(Employee.attendances),
            selectinload(Employee.leaves),
            selectinload(Employee.activities),
            selectinload(Employee.productivity),
            selectinload(Employee.screenshots),
            selectinload(Employee.alerts),
            selectinload(Employee.department),
            selectinload(Employee.team),
        )
        .all()
    )

    return [attach_extra_fields(e) for e in employees]


# Get employee by ID

@router.get("/{emp_id}", response_model=EmployeeResponse)
def get_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    emp = (
        db.query(Employee)
        .options(
            selectinload(Employee.attendances),
            selectinload(Employee.leaves),
            selectinload(Employee.activities),
            selectinload(Employee.productivity),
            selectinload(Employee.alerts),
            selectinload(Employee.department),
            selectinload(Employee.team),
        )
        .filter(Employee.id == emp_id)
        .first()
    )

    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    return attach_extra_fields(emp)


# Update employee by ID

@router.patch("/{emp_id}", response_model=EmployeeResponse)
def update_employee(
    emp_id: int,
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    contact: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),
    department_id: Optional[int] = Form(None),
    team_id: Optional[int] = Form(None),
    profile_picture: UploadFile = File(None),
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    emp = get_employee_by_id(db, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "role": role,
        "contact": contact,
        "designation": designation,
        "department_id": department_id,
        "team_id": team_id,
    }
    update_data = {k: v for k, v in update_data.items() if v is not None}

    picture_path = None
    if profile_picture:
        dest = Path(UPLOAD_DIR) / f"user_{emp_id}_{profile_picture.filename}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(profile_picture.file, buffer)
        picture_path = str(dest.relative_to(Path.cwd()))

    updated_emp = update_profile(db, emp, update_data, picture_path)

    return attach_extra_fields(updated_emp)
