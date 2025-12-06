from fastapi import FastAPI
from database import engine, Base
from routers.tasks import router as tasks_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Task Service")

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(tasks_router)

@app.get("/")
def root():
    return {"message": "Task Service is running"}

@app.get("/health")
def health():
    """Health check endpoint for Kubernetes"""
    return {"status": "healthy", "service": "task-service"}

@app.on_event("startup")
def startup_event():
    logger.info("Task Service started")