from fastapi import APIRouter, Depends
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.auth import get_current_user
from app.schemas.productivity import SummaryMetrics, ProductivityOut
from app.services.productivity_service import (
    calculate_employee_productivity,
    get_summary_metrics,
    compute_and_store_productivity,
    get_productivity_by_employee,
)

router = APIRouter(prefix="/productivity", tags=["productivity"])


# --------------------------------------------------
# Logged-in user's productivity (SYNC)
# --------------------------------------------------
@router.get("/", response_model=ProductivityOut)
def my_productivity(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return calculate_employee_productivity(db, user.id)


# --------------------------------------------------
# Summary metrics (ASYNC)
# --------------------------------------------------
@router.get("/summary", response_model=SummaryMetrics)
async def summary(db: AsyncSession = Depends(get_db)):
    return await get_summary_metrics(db)


# --------------------------------------------------
# Recompute productivity (ASYNC)
# --------------------------------------------------
@router.post("/compute")
async def compute(
    period: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    count = await compute_and_store_productivity(db, period)
    await db.commit()
    return {"status": "ok", "computed": count}


# --------------------------------------------------
# Productivity by employee (ASYNC)
# --------------------------------------------------
@router.get(
    "/employee/{employee_id}",
    response_model=List[ProductivityOut],
)
async def employee_productivity(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_productivity_by_employee(db, employee_id)
