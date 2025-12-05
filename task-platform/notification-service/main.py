from fastapi import FastAPI
from database import engine, Base
from routers.notifications import router as notifications_router

app = FastAPI(title="Notification Service")

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(notifications_router)

@app.get("/")
def root():
    return {"message": "Notification Service is running"}
