from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Task
from pydantic import BaseModel
from datetime import datetime

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
def create_task(task: TaskCreate, x_user_id: int = Header(..., alias="X-User-Id"), db: Session = Depends(get_db)):
    # x_user_id is the creator (supervisor)
    db_task = Task(
        title=task.title,
        description=task.description,
        assigned_to=task.assigned_to,
        created_by=x_user_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/assigned", response_model=list[TaskOut])
def list_assigned(x_user_id: int = Header(..., alias="X-User-Id"), db: Session = Depends(get_db)):
    # Return tasks assigned to the requesting user
    tasks = db.query(Task).filter(Task.assigned_to == x_user_id).all()
    return tasks

@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(task_id: int, status: str, x_user_id: int = Header(..., alias="X-User-Id"), db: Session = Depends(get_db)):
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
def delete_or_reassign(task_id: int, assigned_to: int | None = None, x_user_id: int = Header(..., alias="X-User-Id"), db: Session = Depends(get_db)):
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
