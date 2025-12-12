from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.models.team import Team
from app.models.department import Department
from app.utils.auth import require_roles

router = APIRouter(prefix="/teams", tags=["Teams"])



@router.post("/", response_model=TeamResponse)
def create_team(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin", "Manager"))
):
    
    if team_in.department_id:
        if not db.query(Department).filter(Department.id == team_in.department_id).first():
            raise HTTPException(status_code=400, detail="Department not found")

    team = Team(team_name=team_in.team_name, department_id=team_in.department_id)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team



@router.get("/", response_model=list[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin", "Manager", "Employee"))
):
    return db.query(Team).all()



@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_in: TeamUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin", "Manager"))
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    
    if team_in.department_id is not None:
        dept = db.query(Department).filter(Department.id == team_in.department_id).first()
        if not dept:
            raise HTTPException(status_code=400, detail="Department not found")

    # Apply updates
    update_data = team_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team, key, value)

    db.commit()
    db.refresh(team)
    return team



@router.delete("/{team_id}")
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin", "Manager"))
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    db.delete(team)
    db.commit()
    return {"message": "Team deleted successfully"}
