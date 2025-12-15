from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session, selectinload
from pathlib import Path
from typing import Optional, List
import shutil

from app.core.database import get_db
from app.core.config import UPLOAD_DIR
from app.schemas.employee_schema import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeListResponse,
    EmployeeUpdate,
)
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
# Helper function
# ====================================================
def attach_extra_fields(emp: Employee):
    emp.department_name = emp.department.name if emp.department else None
    emp.team_name = emp.team.name if emp.team else None
    return emp


# ====================================================
# Create new employee (JSON)
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
@router.get("/me", response_model=EmployeeListResponse)
def read_own_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = (
        db.query(Employee)
        .options(
           selectinload(Employee.productivity),
          
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
@router.get("/", response_model=List[EmployeeListResponse])
def list_all_employees(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    employees = (
        db.query(Employee)
        .options(
            
            selectinload(Employee.productivity),
          
            selectinload(Employee.department),
            selectinload(Employee.team),
        )
        .all()
    )

    return [attach_extra_fields(e) for e in employees]


# ====================================================
# Get employee by ID
# ====================================================
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


# ====================================================
# Update employee (JSON ONLY)
# ====================================================
@router.patch("/{emp_id}", response_model=EmployeeUpdate)
def update_employee(
    emp_id: int,
    payload: EmployeeUpdate,  # ⬅ JSON body
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    emp = get_employee_by_id(db, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = payload.model_dump(exclude_unset=True)

    updated_emp = update_profile(db, emp, update_data)

    return attach_extra_fields(updated_emp)


# ====================================================
# Upload profile picture (multipart/form-data)
# ====================================================
@router.post("/{emp_id}/profile-picture", status_code=status.HTTP_200_OK)
def upload_profile_picture(
    emp_id: int,
    profile_picture: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    emp = get_employee_by_id(db, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    allowed_types = {"image/jpeg", "image/png", "image/jpg"}
    if profile_picture.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed",
        )

    upload_dir = Path(UPLOAD_DIR) / "profile_pictures"
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"user_{emp_id}{Path(profile_picture.filename).suffix}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(profile_picture.file, buffer)

    emp.profile_picture = str(file_path.relative_to(Path.cwd()))
    db.commit()
    db.refresh(emp)

    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture": emp.profile_picture,
    }
