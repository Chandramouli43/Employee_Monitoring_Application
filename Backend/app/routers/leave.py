from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.leave import Leave
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.utils.auth import get_current_user

router = APIRouter(prefix="/leave", tags=["Leave Management"])


# ─────────────────────────────────────────────
# DB Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────
# Apply Leave (Logged-in employee only)
@router.post("/apply")
def apply_leave(
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    # --- Validation ---
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date.")

    # Prevent overlapping or duplicate leave entries
    overlap = db.query(Leave).filter(
        Leave.employee_id == current_user.id,
        Leave.status.in_(["Pending", "Approved"]),
        Leave.end_date >= start_date,
        Leave.start_date <= end_date
    ).first()

    if overlap:
        raise HTTPException(status_code=400, detail="You already have leave applied for these dates.")

    # --- Step 1: Create Leave Entry ---
    leave = Leave(
        employee_id=current_user.id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status="Pending",
        applied_on=datetime.utcnow()
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)

    # --- Step 2: Auto-mark Attendance as "On Leave" for the duration ---
    current_date = start_date
    while current_date <= end_date:
        attendance = db.query(Attendance).filter(
            Attendance.employee_id == current_user.id,
            Attendance.date == current_date
        ).first()

        if attendance:
            attendance.status = "On Leave"
            attendance.login_time = None
            attendance.logout_time = None
            attendance.total_hours = "0h 0m"
        else:
            db.add(Attendance(
                employee_id=current_user.id,
                date=current_date,
                status="On Leave",
                total_hours="0h 0m"
            ))
        current_date += timedelta(days=1)

    db.commit()

    return {
        "message": f"Leave request submitted by {current_user.name or current_user.email}",
        "leave_id": leave.id
    }


# ─────────────────────────────────────────────
# Get All Leaves (Admin Only)
@router.get("/all")
def get_all_leaves(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    leaves = (
        db.query(Leave, Employee.name)
        .join(Employee, Leave.employee_id == Employee.id)
        .order_by(Leave.start_date.desc())
        .all()
    )

    return [
        {
            "id": l.Leave.id,
            "employee": l.name,
            "leave_type": l.Leave.leave_type,
            "start_date": str(l.Leave.start_date),
            "end_date": str(l.Leave.end_date),
            "reason": l.Leave.reason,
            "status": l.Leave.status,
            "applied_on": str(l.Leave.applied_on)
        }
        for l in leaves
    ]


# ─────────────────────────────────────────────
# Get My Leaves (Employee only)
@router.get("/my")
def get_my_leaves(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    leaves = db.query(Leave).filter(Leave.employee_id == current_user.id).order_by(Leave.start_date.desc()).all()

    if not leaves:
        return {"message": "No leave records found."}

    return [
        {
            "id": l.id,
            "leave_type": l.leave_type,
            "start_date": str(l.start_date),
            "end_date": str(l.end_date),
            "reason": l.reason,
            "status": l.status,
            "applied_on": str(l.applied_on)
        }
        for l in leaves
    ]


# ─────────────────────────────────────────────
# Approve or Reject Leave (Admin Only)
@router.put("/{leave_id}/{action}")
def update_leave_status(
    leave_id: int,
    action: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    leave = db.query(Leave).filter_by(id=leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found.")
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'.")

    leave.status = "Approved" if action == "approve" else "Rejected"
    leave.approved_by = current_user.id
    db.commit()
    db.refresh(leave)

    # If leave is rejected → revert attendance for those dates
    if action == "reject":
        current_date = leave.start_date
        while current_date <= leave.end_date:
            attendance = db.query(Attendance).filter(
                Attendance.employee_id == leave.employee_id,
                Attendance.date == current_date
            ).first()
            if attendance and attendance.status == "On Leave":
                attendance.status = "Absent"
            current_date += timedelta(days=1)
        db.commit()

    return {"message": f"Leave {action}d successfully", "leave_id": leave.id}


# ─────────────────────────────────────────────
# Monthly Leave Summary (Admin Only)
@router.get("/summary/{year}/{month}")
def get_monthly_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    summary = (
        db.query(
            Employee.name.label("employee"),
            func.count(Leave.id).label("leaves_taken"),
            func.sum(
                func.julianday(Leave.end_date) - func.julianday(Leave.start_date) + 1
            ).label("total_days")
        )
        .join(Employee, Employee.id == Leave.employee_id)
        .filter(func.extract("year", Leave.start_date) == year)
        .filter(func.extract("month", Leave.start_date) == month)
        .filter(Leave.status == "Approved")
        .group_by(Employee.id)
        .all()
    )

    if not summary:
        return {"message": "No leave data for this month."}

    return [
        {
            "employee": s.employee,
            "leaves_taken": int(s.leaves_taken),
            "total_days": int(s.total_days or 0)
        }
        for s in summary
    ]
