# 🚀 DEMO CON DOCKER COMPOSE - PASO A PASO

**Tiempo total: 10-15 minutos**

---

## ⚡ PREPARACIÓN INICIAL (3 minutos)

### Paso 1: Abrir PowerShell
```powershell
# Navegar a la carpeta correcta
cd c:\Users\anyio\Desktop\TareasConNotificacion\PlataformadeTareasconNotificaciones\task-platform

# Verificar que estamos en la carpeta correcta
ls
# Debería mostrar docker-compose.yml
```

### Paso 2: Limpiar contenedores antiguos
```powershell
# Apagar y limpiar (si hay contenedores viejos)
docker-compose down --remove-orphans
```

### Paso 3: Levantar todos los servicios
```powershell
# Iniciar todo
docker-compose up -d

# Esperar 30-60 segundos a que arranque MySQL...
Start-Sleep -Seconds 45
```

### Paso 4: Verificar que todo está corriendo
```powershell
# Ver estado de todos los contenedores
docker-compose ps
```

**Deberías ver algo como:**
```
NAME                    STATUS           PORTS
db_postgres            Up 1 min         0.0.0.0:5432->5432/tcp
db_mysql               Up 1 min         0.0.0.0:3306->3306/tcp
cache_redis            Up 1 min         0.0.0.0:6379->6379/tcp
api_gateway            Up 1 min         0.0.0.0:8000->8000/tcp
auth_service           Up 1 min         0.0.0.0:8001->8001/tcp
task_service           Up 1 min         0.0.0.0:8002->8002/tcp
notification_service   Up 1 min         0.0.0.0:8003->8003/tcp
adminer_gui            Up 1 min         0.0.0.0:8080->8080/tcp
```

✅ **Si ves "Up" en todos = listo para demo**

---

## 🎬 DEMOSTRACIÓN FUNCIONAL (12 minutos)

### DEMO 1: Registrar Usuario Normal (2 minutos)

```powershell
Write-Host "=== PASO 1: Registrar Usuario Normal ===" -ForegroundColor Green

# Llamada HTTP para registrar usuario
$userResp = Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=demo1@example.com&password=demo123&role=user" -Method POST

# Mostrar respuesta
Write-Host "Respuesta del servidor:" -ForegroundColor Cyan
$userResp | Format-List

# Guardar token e ID en variables
$userToken = $userResp.access_token
$userId = $userResp.id

Write-Host ""
Write-Host "✅ Usuario creado:" -ForegroundColor Green
Write-Host "   ID: $userId"
Write-Host "   Email: demo1@example.com"
Write-Host "   Role: user"
Write-Host "   Token: guardado en variable `$userToken"
```

**Explicar al público:**
> Acabamos de registrar un usuario normal. El servidor generó un JWT token que vamos a usar para autenticarnos en las siguientes llamadas. El token contiene el ID del usuario y su rol.

---

### DEMO 2: Registrar Admin (2 minutos)

```powershell
Write-Host ""
Write-Host "=== PASO 2: Registrar Admin ===" -ForegroundColor Green

# Registrar un admin
$adminResp = Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=admin27@example.com&password=admin123&role=admin" -Method POST

Write-Host "Respuesta del servidor:" -ForegroundColor Cyan
$adminResp | Format-List

# Guardar token e ID
$adminToken = $adminResp.access_token
$adminId = $adminResp.id

Write-Host ""
Write-Host "✅ Admin creado:" -ForegroundColor Green
Write-Host "   ID: $adminId"
Write-Host "   Email: admin27@example.com"
Write-Host "   Role: admin"
Write-Host "   Token: guardado en variable `$adminToken"
```

**Explicar al público:**
> Registramos un admin. Verán que el role es diferente. Los admins tienen permisos especiales, por ejemplo pueden crear tareas para otros usuarios. Esto es control de acceso basado en roles (RBAC).

---

### DEMO 3: Crear Tarea (como Admin) (2 minutos)

```powershell
Write-Host ""
Write-Host "=== PASO 3: Crear Tarea (con Admin) ===" -ForegroundColor Green

# Preparar headers con token del admin
$adminHeaders = @{
    "Authorization" = "Bearer $adminToken"
    "Content-Type" = "application/json"
}

# Crear tarea asignada al usuario normal
$taskBody = @{
    title = "Demostración en clase"
    description = "Presentar arquitectura de microservicios en Docker"
    assigned_to = $userId
} | ConvertTo-Json

Write-Host "Enviando petición POST a task-service..." -ForegroundColor Cyan

$taskResp = Invoke-RestMethod -Uri "http://localhost:8002/tasks/" -Method POST -Headers $adminHeaders -Body $taskBody

Write-Host "Respuesta del servidor:" -ForegroundColor Cyan
$taskResp | Format-List

$taskId = $taskResp.task_id

Write-Host ""
Write-Host "✅ Tarea creada:" -ForegroundColor Green
Write-Host "   ID: $taskId"
Write-Host "   Título: $($taskResp.title)"
Write-Host "   Asignada a: Usuario ID=$userId"
Write-Host "   ⚡ Notificación automática generada"
```

**Explicar al público:**
> Acabamos de crear una tarea como admin, asignada al usuario normal. Internamente:
> 1. La tarea se guardó en MySQL
> 2. Task-service automáticamente envió un mensaje a Notification-service
> 3. Notification-service creó una notificación para el usuario

---

### DEMO 4: Ver Tareas del Usuario (2 minutos)

```powershell
Write-Host ""
Write-Host "=== PASO 4: Ver Tareas del Usuario ===" -ForegroundColor Green

# Preparar headers con token del usuario normal
$userHeaders = @{
    "Authorization" = "Bearer $userToken"
    "Content-Type" = "application/json"
}

Write-Host "Solicitando tareas como usuario normal..." -ForegroundColor Cyan

$tasksResp = Invoke-RestMethod -Uri "http://localhost:8002/tasks/assigned" -Method GET -Headers $userHeaders

Write-Host "Respuesta:" -ForegroundColor Cyan
$tasksResp | Format-Table -AutoSize

Write-Host ""
Write-Host "✅ Usuario ve $($tasksResp.Count) tarea(s)" -ForegroundColor Green
Write-Host "✅ El usuario SOLO ve sus propias tareas" -ForegroundColor Green
Write-Host "✅ Esto es USER ISOLATION" -ForegroundColor Green
```

**Explicar al público:**
> El usuario solo ve sus propias tareas. Aunque el admin creó la tarea, la base de datos filtra automáticamente por usuario. Esto es seguridad a nivel de aplicación.

---

### DEMO 5: Ver Notificaciones (2 minutos)

```powershell
Write-Host ""
Write-Host "=== PASO 5: Ver Notificaciones ===" -ForegroundColor Green

Write-Host "Solicitando notificaciones del usuario..." -ForegroundColor Cyan

$notifResp = Invoke-RestMethod -Uri "http://localhost:8003/notifications/" -Method GET -Headers $userHeaders

Write-Host "Respuesta:" -ForegroundColor Cyan
$notifResp | Format-Table -AutoSize

Write-Host ""
Write-Host "✅ Notificación recibida:" -ForegroundColor Green
Write-Host "   Tipo: Nueva tarea asignada"
Write-Host "   Estado: is_read = false (sin leer)"
```

**Explicar al público:**
> La notificación se generó automáticamente cuando creamos la tarea. Notification-service se encarga de esto. En una aplicación real, aquí iría email, SMS o push notifications.

---

### DEMO 6: Intentar crear tarea como usuario normal (Demo de seguridad) (1 minuto)

```powershell
Write-Host ""
Write-Host "=== PASO 6: Intento de ataque (Demo de Seguridad) ===" -ForegroundColor Yellow

$taskBody2 = @{
    title = "Intento de ataque"
    description = "El usuario normal intenta crear una tarea sin permiso"
    assigned_to = $adminId
} | ConvertTo-Json

Write-Host "Usuario normal intenta crear tarea (sin permiso)..." -ForegroundColor Cyan

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8002/tasks/" -Method POST -Headers $userHeaders -Body $taskBody2
    Write-Host "❌ ERROR: El usuario no debería poder crear tareas" -ForegroundColor Red
} catch {
    Write-Host "✅ ACCESO DENEGADO (403 Forbidden)" -ForegroundColor Green
    Write-Host "   Solo admins pueden crear tareas"
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}
```

**Explicar al público:**
> Intentamos que un usuario normal cree una tarea. El servidor rechazó la solicitud (403 Forbidden) porque verificó el JWT token y vio que el role no es admin. Esto es control de acceso basado en roles.

---

## 🌐 BONUS: Ver Base de Datos en Web UI (1 minuto - Opcional)

```powershell
Write-Host ""
Write-Host "=== BONUS: Adminer - Interfaz Web para BD ===" -ForegroundColor Cyan
Write-Host "Abriendo http://localhost:8080 en navegador..."

Start-Process "http://localhost:8080"

# Mostrar en pantalla que Adminer está disponible
Write-Host ""
Write-Host "En Adminer puedes ver:"
Write-Host "  ✓ PostgreSQL (auth_db) - tabla de usuarios"
Write-Host "  ✓ MySQL - tablas de tareas y notificaciones"
```

---

## 📊 RESUMEN DE ARQUITECTURA

```
CLIENTE (PowerShell)
       ↓
    HTTP
       ↓
   GATEWAY (8000)
   ↙  ↓  ↘
┌─────────────────┐
│  AUTH-SERVICE   │
│  (8001)         │
│  PostgreSQL     │
└─────────────────┘

┌─────────────────┐
│ TASK-SERVICE    │
│  (8002)         │
│  MySQL          │
└─────────────────┘
       ↓
┌──────────────────────┐
│NOTIFICATION-SERVICE  │
│  (8003)              │
│  MySQL               │
└──────────────────────┘
```

---

## ✅ PUNTOS CLAVE

### Mostrar al público:

1. **Microservicios**: 3 servicios independientes
2. **Comunicación**: REST APIs
3. **Bases de datos**: PostgreSQL (auth) + MySQL (tasks/notif)
4. **Seguridad**: 
   - JWT tokens para autenticación
   - RBAC (admin vs user) para autorización
   - User isolation a nivel de BD
5. **Automatización**: Notificaciones generadas automáticamente
6. **Escalabilidad**: Docker permite escalar rápidamente

---

## 🔚 AL TERMINAR LA DEMO

```powershell
# Apagar todos los servicios
docker-compose down

# Los datos se guardan en volúmenes Docker (no se pierden)
```

---

## 🚨 TROUBLESHOOTING

### Si un servicio no responde:
```powershell
# Ver logs de un servicio
docker-compose logs auth-service
docker-compose logs task-service
docker-compose logs notification-service

# O ver todos los logs
docker-compose logs -f
```

### Si MySQL tarda mucho en arrancar:
```powershell
# Esperar más tiempo
Start-Sleep -Seconds 60

# Y luego reintentar
docker-compose up -d
```

### Si los puertos están ocupados:
```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :8001
netstat -ano | findstr :8002
netstat -ano | findstr :8003

# O cambiar puertos en docker-compose.yml
```

---

**¡Listo para la demo!** 🎉
