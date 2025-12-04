from fastapi import FastAPI
from routers import auth
from database import Base, engine

app = FastAPI(title="Auth Service")

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# Rutas
app.include_router(auth.router)
