from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.task import Task as TaskModel
from app.schemas.projects import Task as TaskSchema, TaskCreate

router = APIRouter(prefix="/taskmanagement", tags=["Task Management"])


@router.get("/", response_model=List[TaskSchema])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()


@router.post("/", response_model=TaskSchema)
def create_task(request: TaskCreate, db: Session = Depends(get_db)):
    new_task = TaskModel(**request.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.put("/{task_id}", response_model=TaskSchema)
def update_task(task_id: int, request: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in request.dict().items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
