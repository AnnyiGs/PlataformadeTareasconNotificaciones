from fastapi import FastAPI
from database import engine, Base
from routers.notifications import router as notifications_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service")

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(notifications_router)

@app.get("/")
def root():
    return {"message": "Notification Service is running"}

@app.get("/health")
def health():
    """Health check endpoint for Kubernetes"""
    return {"status": "healthy", "service": "notification-service"}

@app.on_event("startup")
def startup_event():
    logger.info("Notification Service started")

