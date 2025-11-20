from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.auth import get_current_user
from app.schemas.productivity import SummaryMetrics
from app.services.productivity_service import (
    calculate_employee_productivity,
    get_summary_metrics,
    compute_and_store_productivity,
    get_productivity_by_employee
)

router = APIRouter(prefix="/productivity", tags=["productivity"])

# ---------------------------
# Sync: get logged-in user's productivity
# ---------------------------
@router.get("/")
def my_productivity(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Fetch productivity metrics for the currently logged-in user.
    """
    return calculate_employee_productivity(db, user.id)

# ---------------------------
# Async: summary of all productivity
# ---------------------------
@router.get("/summary", response_model=SummaryMetrics)
async def summary(db: AsyncSession = Depends(get_db)):
    """
    Get summary metrics for all employees.
    """
    return await get_summary_metrics(db)

# ---------------------------
# Async: recompute productivity aggregates
# ---------------------------
@router.post("/compute")
async def compute(period: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """
    Trigger recompute of productivity aggregates.
    period: optional period string like '2025-10' or '2025-10-21'
    """
    result = await compute_and_store_productivity(db, period=period)
    await db.commit()
    return {"status": "ok", "computed": result}

# ---------------------------
# Async: get productivity for a specific employee
# ---------------------------
@router.get("/employee/{employee_id}")
async def employee_productivity(employee_id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetch productivity metrics for a specific employee by ID.
    """
    return await get_productivity_by_employee(db, employee_id)
