from fastapi import FastAPI
from database import engine, Base
from routers.tasks import router as tasks_router

app = FastAPI(title="Task Service")

# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(tasks_router)

@app.get("/")
def root():
    return {"message": "Task Service is running"}
