from fastapi import FastAPI
from routers import auth
from database import Base, engine
from sqlalchemy import inspect, text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auth Service")

# Crear tablas si no existen y asegurar columna role
def ensure_role_column():
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("users")]
    if "role" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'user'"))

Base.metadata.create_all(bind=engine)
ensure_role_column()

# Rutas
app.include_router(auth.router)

@app.get("/health")
def health():
    """Health check endpoint for Kubernetes"""
    return {"status": "healthy", "service": "auth-service"}

@app.on_event("startup")
def startup_event():
    logger.info("Auth Service started")

