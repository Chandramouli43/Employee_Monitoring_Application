# app/routers/activity_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.core.database import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/activities", tags=["activities"])

# ---------------------------
# Log / Create activity
# ---------------------------
@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_activity = Activity(
        employee_id=current_user.id,
        department_id=current_user.department_id,
        team_id=current_user.team_id,
        activity_type=activity.activity_type,
        description=activity.description,
        timestamp=datetime.utcnow()
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

# ---------------------------
# Get logged-in employee's activities
# ---------------------------
@router.get("/me", response_model=List[ActivityResponse])
def get_my_activities(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(Activity)
        .filter(Activity.employee_id == current_user.id)
        .order_by(Activity.timestamp.desc())
        .all()
    )

# ---------------------------
# Get activities by employee (optional date range)
# ---------------------------
@router.get("/employee/{employee_id}", response_model=List[ActivityResponse])
def get_activities_by_employee(
    employee_id: int,
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Activity).filter(Activity.employee_id == employee_id)
    
    if start:
        start_dt = datetime.fromisoformat(start)
        query = query.filter(Activity.timestamp >= start_dt)
    if end:
        end_dt = datetime.fromisoformat(end)
        query = query.filter(Activity.timestamp <= end_dt)
    
    return query.order_by(Activity.timestamp.desc()).all()
