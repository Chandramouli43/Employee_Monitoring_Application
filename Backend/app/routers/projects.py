from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session
import app.models
import app.core.database as database
from app.schemas.projects import Project, ProjectCreate


router = APIRouter()

get_db = database.get_db

@router.post("/", response_model=Project)
def create_project(project: ProjectCreate, db: Session = Depends(database.get_db)):
    new_project = app.models.Project(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=list[Project])
def get_projects(db: Session = Depends(database.get_db)):
    return db.query(app.models.Project).all()

# 🟡 Update project
@router.put("/{project_id}", response_model=Project)
def update_project(project_id: int, request: ProjectCreate, db: Session = Depends(get_db)):
    project = db.query(app.models.Project).filter(app.models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in request.dict().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

# 🔴 Delete project
@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(app.models.Project).filter(app.models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
