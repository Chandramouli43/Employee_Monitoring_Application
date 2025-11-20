# app/services/productivity_service.py

from typing import List, Optional
from datetime import datetime

# Async imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Sync imports
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.productivity import Productivity
from app.models.activity import Activity
from app.schemas.productivity import SummaryMetrics

# ==================================================
# 🔹 ASYNC FUNCTIONS (AsyncSession)
# ==================================================

async def get_summary_metrics(db: AsyncSession) -> SummaryMetrics:
    """Compute simple summary metrics across all employees asynchronously."""
    res_avg = await db.execute(select(func.avg(Employee.productivity_score)))
    avg_score = res_avg.scalar() or 0.0

    res_hours = await db.execute(select(func.avg(Employee.hours_logged)))
    avg_hours = res_hours.scalar() or 0.0

    res_tasks = await db.execute(select(func.sum(Employee.tasks_completed)))
    total_tasks = res_tasks.scalar() or 0

    return SummaryMetrics(
        overall_score=round(float(avg_score), 2),
        average_hours=round(float(avg_hours), 2),
        tasks_completed=int(total_tasks),
    )

async def compute_and_store_productivity(db: AsyncSession, period: Optional[str] = None) -> int:
    """
    Compute productivity for all employees and store it in Productivity table.
    If period is None, use current date.
    """
    if not period:
        period = datetime.utcnow().strftime("%Y-%m-%d")  # default daily snapshot

    q = await db.execute(select(Employee))
    employees = q.scalars().all()
    count = 0
    for e in employees:
        p = Productivity(
            employee_id=e.id,
            period=period,
            average_score=e.productivity_score or 0.0,
            tasks_completed=e.tasks_completed or 0,
            hours_logged=e.hours_logged or 0.0
        )
        db.add(p)
        count += 1
    await db.flush()
    return count

async def get_productivity_by_employee(db: AsyncSession, employee_id: int) -> List[Productivity]:
    """Get productivity records for a specific employee asynchronously."""
    q = await db.execute(
        select(Productivity)
        .where(Productivity.employee_id == employee_id)
        .order_by(Productivity.created_at.desc())
    )
    return q.scalars().all()

# ==================================================
# 🔹 SYNC FUNCTIONS (Session)
# ==================================================

def calculate_employee_productivity(db: Session, employee_id: int) -> Productivity:
    """
    Compute a productivity score for a specific employee synchronously,
    based on their activities marked as productive.
    """
    activities = db.query(Activity).filter(Activity.employee_id == employee_id).all()
    total = len(activities)
    productive_count = sum(1 for a in activities if getattr(a, "productive", "Yes") == "Yes")
    score = round((productive_count / total) * 100, 2) if total else 0

    db_productivity = Productivity(
        employee_id=employee_id,
        score=score,
        timestamp=datetime.utcnow()
    )
    db.add(db_productivity)
    db.commit()
    db.refresh(db_productivity)
    return db_productivity
