from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.alert_service import stats_summary

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/summary")
async def summary(db: AsyncSession = Depends(get_db)):
    return await stats_summary(db)
