from fastapi import FastAPI
from routers import auth
from database import Base, engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auth Service")

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Rutas
app.include_router(auth.router)

@app.get("/health")
def health():
    """Health check endpoint for Kubernetes"""
    return {"status": "healthy", "service": "auth-service"}

@app.on_event("startup")
def startup_event():
    logger.info("Auth Service started")

