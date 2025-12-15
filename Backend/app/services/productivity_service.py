from typing import List, Optional
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.employee import Employee
from app.models.productivity import Productivity
from app.models.activity import Activity
from app.schemas.productivity import SummaryMetrics


# ==================================================
# ASYNC SERVICES
# ==================================================

async def get_summary_metrics(db: AsyncSession) -> SummaryMetrics:
    avg_score = (
        await db.execute(select(func.avg(Employee.productivity_score)))
    ).scalar() or 0.0

    avg_hours = (
        await db.execute(select(func.avg(Employee.hours_logged)))
    ).scalar() or 0.0

    total_tasks = (
        await db.execute(select(func.sum(Employee.tasks_completed)))
    ).scalar() or 0

    return SummaryMetrics(
        overall_score=round(float(avg_score), 2),
        average_hours=round(float(avg_hours), 2),
        tasks_completed=int(total_tasks),
    )


async def compute_and_store_productivity(
    db: AsyncSession,
    period: Optional[str] = None,
) -> int:
    if not period:
        period = str(date.today())

    result = await db.execute(select(Employee))
    employees = result.scalars().all()

    count = 0
    for e in employees:
        record = Productivity(
            employee_id=e.id,
            department_id=e.department_id,
            team_id=e.team_id,
            period=period,
            average_score=e.productivity_score or 0.0,
            tasks_completed=e.tasks_completed or 0,
            hours_logged=e.hours_logged or 0.0,
        )
        db.add(record)
        count += 1

    await db.flush()
    return count


async def get_productivity_by_employee(
    db: AsyncSession,
    employee_id: int,
) -> List[Productivity]:
    result = await db.execute(
        select(Productivity)
        .where(Productivity.employee_id == employee_id)
        .order_by(Productivity.created_at.desc())
    )
    return result.scalars().all()


# ==================================================
# SYNC SERVICES
# ==================================================

def calculate_employee_productivity(
    db: Session,
    employee_id: int,
) -> Productivity:
    activities = (
        db.query(Activity)
        .filter(Activity.employee_id == employee_id)
        .all()
    )

    total = len(activities)
    productive_count = sum(
        1 for a in activities if getattr(a, "productive", "Yes") == "Yes"
    )

    score = round((productive_count / total) * 100, 2) if total else 0.0

    emp = db.query(Employee).get(employee_id)

    record = Productivity(
        employee_id=employee_id,
        department_id=emp.department_id,
        team_id=emp.team_id,
        score=score,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record
