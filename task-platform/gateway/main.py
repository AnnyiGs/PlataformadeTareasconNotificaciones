from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import jwt
import json
import os
import logging
import time
from typing import Optional

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="Gateway unificado para microservicios de tareas",
    version="1.0.0"
)

# Configuración CORS - permite que frontends accedan a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs de servicios backend (configurables por variables de entorno)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://task-service:8002")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8003")

# Clave secreta JWT (debe ser la misma que en auth-service)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-jwt-key-change-in-production-12345")
JWT_ALGORITHM = "HS256"

# Cliente HTTP asíncrono para hacer proxy requests
http_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log todas las requests con duración y status code"""
    start_time = time.time()
    
    # Log request entrante
    logger.info(f"→ {request.method} {request.url.path} from {request.client.host}")
    
    response = await call_next(request)
    
    # Calcular duración
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        f"← {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    return response


# Función para validar JWT y extraer user_id
async def validate_jwt_token(request: Request) -> Optional[dict]:
    """
    Valida el token JWT del header Authorization.
    Retorna el payload decodificado o None si no hay token.
    Lanza HTTPException si el token es inválido.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return None
    
    try:
        # Extraer token del formato "Bearer <token>"
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = auth_header.replace("Bearer ", "")
        
        # Decodificar y validar JWT
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Extraer user_id del claim "sub"
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        logger.info(f"✓ JWT validado para user_id: {user_id}")
        
        return {**payload, "user_id": user_id}  # Agregar user_id para facilitar acceso
    
    except jwt.ExpiredSignatureError:
        logger.warning("✗ JWT expirado")
        raise HTTPException(status_code=401, detail="Token has expired")
    
    except jwt.InvalidTokenError as e:
        logger.warning(f"✗ JWT inválido: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check del gateway"""
    return {
        "status": "healthy",
        "service": "gateway",
        "backends": {
            "auth": AUTH_SERVICE_URL,
            "task": TASK_SERVICE_URL,
            "notification": NOTIFICATION_SERVICE_URL
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """Información del gateway"""
    return {
        "message": "API Gateway - Task Platform",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth/*",
            "tasks": "/api/tasks/*",
            "notifications": "/api/notifications/*"
        },
        "docs": "/docs"
    }


# ============================================================================
# PROXY ROUTES - Auth Service
# ============================================================================

@app.post("/api/auth/register")
async def proxy_register(request: Request):
    """Proxy para registro de usuarios (sin autenticación requerida)"""
    body = await request.json()
    
    try:
        # Auth-service usa query params, no body
        response = await http_client.post(
            f"{AUTH_SERVICE_URL}/auth/register",
            params={
                "email": body.get("email"),
                "password": body.get("password")
            }
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Error conectando a auth-service: {str(e)}")
        raise HTTPException(status_code=503, detail="Auth service unavailable")


@app.post("/api/auth/login")
async def proxy_login(request: Request):
    """Proxy para login (sin autenticación requerida)"""
    body = await request.json()
    
    try:
        # Auth-service usa query params, no body
        response = await http_client.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            params={
                "email": body.get("email"),
                "password": body.get("password")
            }
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Error conectando a auth-service: {str(e)}")
        raise HTTPException(status_code=503, detail="Auth service unavailable")


# ============================================================================
# PROXY ROUTES - Task Service (requieren autenticación)
# ============================================================================

@app.get("/api/tasks")
async def proxy_get_tasks(request: Request):
    """Proxy para listar tareas (requiere JWT)"""
    # Validar JWT y extraer user_id
    payload = await validate_jwt_token(request)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = payload.get("user_id")
    auth_header = request.headers.get("Authorization", "")
    
    try:
        # Hacer request al task-service con JWT
        response = await http_client.get(
            f"{TASK_SERVICE_URL}/tasks",
            headers={
                "Authorization": auth_header,
                "X-User-Id": str(user_id)
            }
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Error conectando a task-service: {str(e)}")
        raise HTTPException(status_code=503, detail="Task service unavailable")


@app.post("/api/tasks")
async def proxy_create_task(request: Request):
    """Proxy para crear tarea (requiere JWT)"""
    # Validar JWT
    payload = await validate_jwt_token(request)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = payload.get("user_id")
    
    # Leer body como bytes y decodificar manualmente
    try:
        body_bytes = await request.body()
        body = json.loads(body_bytes.decode('utf-8'))
    except Exception as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Agregar assigned_to automáticamente si no está presente
    if "assigned_to" not in body:
        body["assigned_to"] = int(user_id)
    
    # Obtener token original del header Authorization
    auth_header = request.headers.get("Authorization", "")
    
    try:
        response = await http_client.post(
            f"{TASK_SERVICE_URL}/tasks",
            json=body,
            headers={
                "Authorization": auth_header,  # Propagar JWT al backend
                "X-User-Id": str(user_id)       # También enviar X-User-Id por compatibilidad
            }
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Error conectando a task-service: {str(e)}")
        raise HTTPException(status_code=503, detail="Task service unavailable")


@app.get("/api/tasks/{task_id}")
async def proxy_get_task(task_id: int, request: Request):
    """Proxy para obtener tarea específica (requiere JWT)"""
    payload = await validate_jwt_token(request)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = payload.get("user_id")
    auth_header = request.headers.get("Authorization", "")
    
    try:
        response = await http_client.get(
            f"{TASK_SERVICE_URL}/tasks/{task_id}",
            headers={
                "Authorization": auth_header,
                "X-User-Id": str(user_id)
            }
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Error conectando a task-service: {str(e)}")
        raise HTTPException(status_code=503, detail="Task service unavailable")


@app.put("/api/tasks/{task_id}")
async def proxy_update_task(task_id: int, request: Request):
    """Proxy para actualizar tarea (requiere JWT)"""
    payload = await validate_jwt_token(request)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = payload.get("user_id")
    body = await request.json()
    
    try:
        response = await http_client.put(
            f"{TASK_SERVICE_URL}/tasks/{task_id}",
            json=body,
            headers={"X-User-Id": str(user_id)}
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Error conectando a task-service: {str(e)}")
        raise HTTPException(status_code=503, detail="Task service unavailable")


@app.delete("/api/tasks/{task_id}")
async def proxy_delete_task(task_id: int, request: Request):
    """Proxy para eliminar tarea (requiere JWT)"""
    payload = await validate_jwt_token(request)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = payload.get("user_id")
    
    try:
        response = await http_client.delete(
            f"{TASK_SERVICE_URL}/tasks/{task_id}",
            headers={"X-User-Id": str(user_id)}
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Error conectando a task-service: {str(e)}")
        raise HTTPException(status_code=503, detail="Task service unavailable")


# ============================================================================
# PROXY ROUTES - Notification Service (requieren autenticación)
# ============================================================================

@app.get("/api/notifications")
async def proxy_get_notifications(request: Request):
    """Proxy para listar notificaciones (requiere JWT)"""
    payload = await validate_jwt_token(request)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = payload.get("user_id")
    auth_header = request.headers.get("Authorization", "")
    
    try:
        response = await http_client.get(
            f"{NOTIFICATION_SERVICE_URL}/notifications",
            headers={
                "Authorization": auth_header,
                "X-User-Id": str(user_id)
            }
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Error conectando a notification-service: {str(e)}")
        raise HTTPException(status_code=503, detail="Notification service unavailable")


@app.put("/api/notifications/{notification_id}/read")
async def proxy_mark_notification_read(notification_id: int, request: Request):
    """Proxy para marcar notificación como leída (requiere JWT)"""
    payload = await validate_jwt_token(request)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = payload.get("user_id")
    
    try:
        response = await http_client.put(
            f"{NOTIFICATION_SERVICE_URL}/notifications/{notification_id}/read",
            headers={"X-User-Id": str(user_id)}
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except httpx.RequestError as e:
        logger.error(f"Error conectando a notification-service: {str(e)}")
        raise HTTPException(status_code=503, detail="Notification service unavailable")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log cuando el gateway inicia"""
    logger.info("=" * 80)
    logger.info("🚪 API Gateway iniciado")
    logger.info(f"Auth Service: {AUTH_SERVICE_URL}")
    logger.info(f"Task Service: {TASK_SERVICE_URL}")
    logger.info(f"Notification Service: {NOTIFICATION_SERVICE_URL}")
    logger.info("=" * 80)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cerrar conexiones HTTP al apagar"""
    await http_client.aclose()
    logger.info("🚪 API Gateway detenido")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
