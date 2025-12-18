# app/routers/admin_productivity_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict

from app.core.database import get_db
from app.services.admin_productivity_service import get_org_summary, get_team_summary, get_department_summary
from app.schemas.admin_schemas import OrgSummary
from app.utils.auth import require_roles

router = APIRouter(prefix="/admin/productivity", tags=["Admin Productivity"])

@router.get("/overview", response_model=OrgSummary)
def overview(db: Session = Depends(get_db), _=Depends(require_roles("Admin"))):
    return get_org_summary(db)

@router.get("/team/{team_id}")
def team_summary(team_id: int, db: Session = Depends(get_db), _=Depends(require_roles("Admin"))):
    return get_team_summary(db, team_id)

@router.get("/department/{department_id}")
def department_summary(department_id: int, db: Session = Depends(get_db), _=Depends(require_roles("Admin"))):
    return get_department_summary(db, department_id)
