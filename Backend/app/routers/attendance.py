from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone, date
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.attendance import Attendance
from app.models.leave import Leave          # ✅ added to cross-check leave
from app.models.employee import Employee
from app.utils.auth import get_current_user
from app.schemas.attendance import AttendanceResponse
from app.core.database import get_db

router = APIRouter(prefix="/attendance", tags=["Attendance Management"])
# Punch IN (blocked if on leave)
@router.post("/punch_in", response_model=AttendanceResponse)
def punch_in(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    today = datetime.now(timezone.utc).date()

    # 🚫 Check if user is on approved or pending leave
    on_leave = (
        db.query(Leave)
        .filter(
            Leave.employee_id == current_user.id,
            Leave.start_date <= today,
            Leave.end_date >= today,
            Leave.status.in_(["Pending", "Approved"])
        )
        .first()
    )
    if on_leave:
        raise HTTPException(status_code=400, detail="Cannot punch in — you are on leave today.")

    existing = (
        db.query(Attendance)
        .filter(Attendance.employee_id == current_user.id, Attendance.date == today)
        .first()
    )

    # 🚫 Block punching if marked 'On Leave'
    if existing and existing.status == "On Leave":
        raise HTTPException(status_code=400, detail="Cannot punch in while on leave.")
    if existing:
        raise HTTPException(status_code=400, detail="Already punched in today.")

    record = Attendance(
        employee_id=current_user.id,
        date=today,
        login_time=datetime.now(timezone.utc),
        status="Present"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# ─────────────────────────────────────────────
# Punch OUT (blocked if on leave)
@router.post("/punch_out", response_model=AttendanceResponse)
def punch_out(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    today = datetime.now(timezone.utc).date()

    # 🚫 Block if leave exists
    on_leave = (
        db.query(Leave)
        .filter(
            Leave.employee_id == current_user.id,
            Leave.start_date <= today,
            Leave.end_date >= today,
            Leave.status.in_(["Pending", "Approved"])
        )
        .first()
    )
    if on_leave:
        raise HTTPException(status_code=400, detail="Cannot punch out — you are on leave today.")

    record = (
        db.query(Attendance)
        .filter(Attendance.employee_id == current_user.id, Attendance.date == today)
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="No punch-in found for today.")
    if record.logout_time:
        raise HTTPException(status_code=400, detail="Already punched out today.")
    if record.status == "On Leave":
        raise HTTPException(status_code=400, detail="Cannot punch out while on leave.")

    record.logout_time = datetime.now(timezone.utc)
    record.total_hours = calculate_hours(record.login_time, record.logout_time)
    record.status = "Present"
    db.commit()
    db.refresh(record)
    return record

# ─────────────────────────────────────────────
# Get today's attendance
@router.get("/today", response_model=AttendanceResponse)
def get_today_attendance(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    today = datetime.now(timezone.utc).date()

    record = (
        db.query(Attendance)
        .filter(Attendance.employee_id == current_user.id, Attendance.date == today)
        .first()
    )

    if not record:
        # Check if on leave today
        on_leave = (
            db.query(Leave)
            .filter(
                Leave.employee_id == current_user.id,
                Leave.start_date <= today,
                Leave.end_date >= today,
                Leave.status.in_(["Pending", "Approved"])
            )
            .first()
        )
        if on_leave:
            return AttendanceResponse(
                id=0,
                date=today,
                login_time=None,
                logout_time=None,
                total_hours="0h 0m",
                status="On Leave",
            )

        return AttendanceResponse(
            id=0,
            date=today,
            login_time=None,
            logout_time=None,
            total_hours="0h 0m",
            status="Not Punched In",
        )

    return record

# ─────────────────────────────────────────────
# Attendance summary for employee
@router.get("/summary", response_model=List[AttendanceResponse])
def get_summary(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(30, ge=1, le=100)
):
    query = db.query(Attendance).filter(Attendance.employee_id == current_user.id)

    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)

    records = query.order_by(Attendance.date.desc()).limit(limit).all()
    return records
