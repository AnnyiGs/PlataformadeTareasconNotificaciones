from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Notification
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["Notifications"])

class NotifyIn(BaseModel):
    user_id: int
    message: str
    task_id: int | None = None

class NotificationOut(BaseModel):
    id: int
    user_id: int
    message: str
    task_id: int | None = None
    read: bool
    created_at: str

@router.post("/notify")
def notify(payload: NotifyIn, db: Session = Depends(get_db)):
    notif = Notification(user_id=payload.user_id, message=payload.message, task_id=payload.task_id)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return {"message": "Notification created", "id": notif.id}

@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(x_user_id: int = Header(..., alias="X-User-Id"), db: Session = Depends(get_db)):
    notes = db.query(Notification).filter(Notification.user_id == x_user_id).order_by(Notification.created_at.desc()).all()
    return notes
