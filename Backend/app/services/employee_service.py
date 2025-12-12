# app/services/employee_service.py

from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.employee import Employee
from app.models.department import Department
from app.models.team import Team
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_employee(db: Session, employee_data: dict) -> Employee:
    """Create a new employee synchronously."""
    # Hash password
    employee_data.password = get_password_hash(employee_data.password)

    # Handle department
    dept_id = employee_data.department_id
    if dept_id:
        dept = db.query(Department).filter(Department.id == dept_id).first()
        if not dept:
            dept = Department(id=dept_id, name=f"Dept-{dept_id}")
            db.add(dept)
            db.commit()
            db.refresh(dept)

    # Handle team
    team_id = employee_data.team_id
    if team_id:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            team = Team(id=team_id, name=f"Team-{team_id}", department_id=dept_id)
            db.add(team)
            db.commit()
            db.refresh(team)

    # Create employee
    new_employee = Employee(**employee_data.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.email == email).first()

def get_employee_by_id(db: Session, emp_id: int) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.id == emp_id).first()

def update_profile(db: Session, emp: Employee, updates: dict, profile_picture_path: str | None = None) -> Employee:
    """Update employee profile fields."""
    for k, v in updates.items():
        setattr(emp, k, v)
    if profile_picture_path:
        emp.profile_picture = profile_picture_path
    db.commit()
    db.refresh(emp)
    return emp
