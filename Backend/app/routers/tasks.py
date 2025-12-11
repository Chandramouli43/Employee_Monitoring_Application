from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
import app.models
import app.core.database as database
from app.schemas.projects import Task, TaskCreate


router = APIRouter()

get_db = database.get_db

# 🟢 Get all tasks
@router.get("/", response_model=List[Task])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(app.models.Task).all()

# 🟢 Create a new task
@router.post("/", response_model=Task)
def create_task(request: TaskCreate, db: Session = Depends(get_db)):
    new_task = app.models.Task(**request.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# 🟡 Update task
@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, request: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(app.models.Task).filter(app.models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in request.dict().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

# 🔴 Delete task
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(app.models.Task).filter(app.models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
