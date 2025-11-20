from pydantic import BaseModel
from datetime import date

class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = "Active"

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    project_id: int | None = None
    assigned_to: str | None = None
    status: str | None = "Pending"
    due_date: date | None = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    class Config:
        orm_mode = True


class NotificationBase(BaseModel):
    message: str
    is_read: bool | None = False

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    class Config:
        orm_mode = True
