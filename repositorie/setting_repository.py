from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.setting import NotificationSetting

async def get_all_settings(db: AsyncSession) -> List[NotificationSetting]:
    res = await db.execute(select(NotificationSetting))
    return res.scalars().all()
