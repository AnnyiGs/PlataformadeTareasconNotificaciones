from fastapi import APIRouter, Depends, Header, HTTPException, Query, Path
from sqlalchemy.orm import Session
from database import get_db
from models import Notification
from pydantic import BaseModel
from datetime import datetime
from datetime import timedelta

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
    created_at: datetime

@router.post("/notify")
def notify(payload: NotifyIn, db: Session = Depends(get_db)):
    notif = Notification(user_id=payload.user_id, message=payload.message, task_id=payload.task_id)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return {"message": "Notification created", "id": notif.id}

@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(
    x_user_id: int = Header(..., alias="X-User-Id"),
    unread_only: bool = Query(False, description="If true, return only unread notifications"),
    since_minutes: int | None = Query(None, description="If provided, return notifications created within the last N minutes"),
    db: Session = Depends(get_db),
):
    q = db.query(Notification).filter(Notification.user_id == x_user_id)
    if unread_only:
        q = q.filter(Notification.read == False)
    if since_minutes is not None:
        cutoff = datetime.utcnow() - timedelta(minutes=since_minutes)
        q = q.filter(Notification.created_at >= cutoff)
    notes = q.order_by(Notification.created_at.desc()).all()
    return notes


@router.patch("/notifications/{notif_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notif_id: int = Path(..., description="ID of the notification to mark read"),
    x_user_id: int = Header(..., alias="X-User-Id"),
    db: Session = Depends(get_db),
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notif.user_id != x_user_id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this notification")
    notif.read = True
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif
