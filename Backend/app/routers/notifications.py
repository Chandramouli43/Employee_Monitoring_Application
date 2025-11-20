from fastapi import APIRouter, Depends, HTTPException 
from sqlalchemy.orm import Session
import app.models, schemas
import app.core.database as database
from datetime import date
from app.schemas.projects import Notification, NotificationCreate

router = APIRouter()

get_db = database.get_db
@router.post("/", response_model=Notification)
def create_notification(note: NotificationCreate, db: Session = Depends(database.get_db)):
    new_note = app.models.Notification(**note.dict(), created_at=date.today())
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@router.get("/", response_model=list[Notification])
def get_notifications(db: Session = Depends(database.get_db)):
    return db.query(app.models.Notification).all()

# 🟡 Update notification
@router.put("/{notification_id}", response_model=Notification)
def update_notification(notification_id: int, request: NotificationCreate, db: Session = Depends(get_db)):
    notification = db.query(app.models.Notification).filter(app.models.Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    for key, value in request.dict().items():
        setattr(notification, key, value)
    db.commit()
    db.refresh(notification)
    return notification

# 🔴 Delete notification
@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(app.models.Notification).filter(app.models.Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted successfully"}
