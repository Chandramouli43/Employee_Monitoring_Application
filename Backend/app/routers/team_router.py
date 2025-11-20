from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.team import TeamCreate, TeamResponse
from app.models.team import Team
from app.models.department import Department
from app.utils.auth import require_roles

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=TeamResponse)
def create_team(team_in: TeamCreate, db: Session = Depends(get_db), _: object = Depends(require_roles("Admin","Manager"))):
    if team_in.department_id:
        if not db.query(Department).filter(Department.id == team_in.department_id).first():
            raise HTTPException(status_code=400, detail="Department not found")
    team = Team(name=team_in.name, department_id=team_in.department_id)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

@router.get("/", response_model=list[TeamResponse])
def list_teams(db: Session = Depends(get_db), _ = Depends(require_roles("Admin","Manager","Employee"))):
    return db.query(Team).all()
