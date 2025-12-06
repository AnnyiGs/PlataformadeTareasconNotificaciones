from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Task
from security import verify_token
from pydantic import BaseModel
import requests
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8003")

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to: int

class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    assigned_to: int
    created_by: int
    created_at: datetime

@router.post("/", response_model=TaskOut)
def create_task(task: TaskCreate, token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    # token["user_id"] is the creator (supervisor)
    x_user_id = token["user_id"]
    db_task = Task(
        title=task.title,
        description=task.description,
        assigned_to=task.assigned_to,
        created_by=x_user_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    # Notify assigned user via Notification Service
    try:
        notif_payload = {
            "user_id": db_task.assigned_to,
            "message": f"Nueva tarea asignada: {db_task.title}",
            "task_id": db_task.id,
        }
        response = requests.post(f"{NOTIFICATION_SERVICE_URL}/notify", json=notif_payload, timeout=2)
        response.raise_for_status()
        logger.info(f"Notification sent for task {db_task.id}")
    except Exception as e:
        # avoid failing task creation if notification fails
        logger.warning(f"Failed to send notification for task {db_task.id}: {str(e)}")
    return db_task

@router.get("/assigned", response_model=list[TaskOut])
def list_assigned(token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    # Return tasks assigned to the requesting user
    x_user_id = token["user_id"]
    tasks = db.query(Task).filter(Task.assigned_to == x_user_id).all()
    return tasks

@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(task_id: int, status: str, token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    x_user_id = token["user_id"]
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Only assigned user can update status
    if task.assigned_to != x_user_id:
        raise HTTPException(status_code=403, detail="Not allowed to update status")
    task.status = status
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_or_reassign(task_id: int, assigned_to: int | None = None, token: dict = Depends(verify_token), db: Session = Depends(get_db)):
    # For now assume the requester is supervisor (no role check). If assigned_to provided, reassign, else delete
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if assigned_to is not None:
        task.assigned_to = assigned_to
        db.commit()
        db.refresh(task)
        return {"message": "Task reassigned", "task_id": task.id}
    else:
        db.delete(task)
        db.commit()
        return {"message": "Task deleted", "task_id": task_id}
