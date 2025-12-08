# 🎯 GUÍA DE DEMOSTRACIÓN - PLATAFORMA DE TAREAS CON NOTIFICACIONES

## ⚡ OPCIÓN A: Demo con Docker Compose (RECOMENDADO - MÁS RÁPIDO) 

### 📋 Preparación Previa (2-3 minutos)

#### 1. Verificar que Docker Desktop esté corriendo
```powershell
docker --version
docker ps
```

#### 2. Navegar a la carpeta correcta
```powershell
cd c:\Users\anyio\Desktop\TareasConNotificacion\PlataformadeTareasconNotificaciones\task-platform
```

#### 3. Limpiar contenedores antiguos (si existen)
```powershell
docker-compose down --remove-orphans
```

#### 4. Levantar todos los servicios
```powershell
docker-compose up -d
```

**Esperar 30-60 segundos** a que las bases de datos arranquen completamente.

#### 5. Verificar que todo está corriendo
```powershell
docker-compose ps
```

**Todos deben mostrar `Up` o `healthy`**

---

## 🎬 DEMOSTRACIÓN CON DOCKER COMPOSE (10-15 minutos)

### PASO 1: Verificar servicios (1 minuto)

**En PowerShell:**
```powershell
# Ver todos los contenedores corriendo
docker-compose ps

# Mostrar logs de los servicios
docker-compose logs gateway
```

**Debería ver:**
- gateway: corriendo en puerto 8000
- auth-service: corriendo en puerto 8001
- task-service: corriendo en puerto 8002
- notification-service: corriendo en puerto 8003
- postgres: base de datos para auth
- mysql: base de datos para tasks/notifications
- redis: caché
- adminer: herramienta web para ver BD

---

### PASO 2: Registrar Usuario Normal (2 minutos)

**En PowerShell:**
```powershell
# Registrar un usuario normal
$userResp = Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=demo1@example.com&password=demo123&role=user" -Method POST
$userResp | Format-List

# Guardar token y ID
$userToken = $userResp.access_token
$userId = $userResp.id

Write-Host "✅ Usuario creado: ID=$userId"
Write-Host "✅ Token guardado para próximos pasos"
```

**Explicar:**
- Se registra un usuario normal
- Se genera un JWT token automáticamente
- El token expira en 8 horas
- Se guarda el ID para asignar tareas

---

### PASO 3: Registrar Admin (2 minutos)

**En PowerShell:**
```powershell
# Registrar un admin
$adminResp = Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=admin27@example.com&password=admin123&role=admin" -Method POST
$adminResp | Format-List

# Guardar token y ID
$adminToken = $adminResp.access_token
$adminId = $adminResp.id

Write-Host "✅ Admin creado: ID=$adminId"
Write-Host "✅ Token guardado para crear tareas"
```

**Explicar:**
- Solo un admin puede crear tareas para otros usuarios
- El usuario normal NO puede crear tareas
- Esto demuestra control de acceso basado en roles (RBAC)

---

### PASO 4: Crear una Tarea (2 minutos)

**En PowerShell:**
```powershell
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

$taskResp = Invoke-RestMethod -Uri "http://localhost:8002/tasks/" -Method POST -Headers $adminHeaders -Body $taskBody
$taskResp | Format-List

$taskId = $taskResp.task_id
Write-Host "✅ Tarea ID=$taskId creada"
Write-Host "✅ Asignada a usuario ID=$userId"
```

**Mostrar en pantalla:**
- La tarea se crea en MySQL
- Se genera una notificación automática
- Task-service → Notification-service (comunicación inter-servicios)

---

### PASO 5: Ver Tareas del Usuario (2 minutos)

**En PowerShell:**
```powershell
# Preparar headers con token del usuario normal
$userHeaders = @{
    "Authorization" = "Bearer $userToken"
    "Content-Type" = "application/json"
}

# Ver tareas asignadas al usuario
$tasksResp = Invoke-RestMethod -Uri "http://localhost:8002/tasks/assigned" -Method GET -Headers $userHeaders
$tasksResp | Format-Table -AutoSize

Write-Host "✅ Usuario ve solo sus tareas"
Write-Host "✅ Esto demuestra USER ISOLATION"
```

**Explicar:**
- El usuario normal solo ve sus tareas
- No puede ver tareas de otros usuarios
- Cada usuario está aislado en la base de datos

---

### PASO 6: Ver Notificaciones (2 minutos)

**En PowerShell:**
```powershell
# Ver notificaciones del usuario
$notifResp = Invoke-RestMethod -Uri "http://localhost:8003/notifications/" -Method GET -Headers $userHeaders
$notifResp | Format-Table -AutoSize

Write-Host "✅ El usuario recibió notificación automática"
Write-Host "✅ Notificación: Nueva tarea asignada"
```

**Mostrar:**
- Notificación generada automáticamente al crear la tarea
- Contiene detalles de la tarea
- `is_read: false` (sin leer)

---

### PASO 7: Acceso Denegado (Demo de Seguridad - 1 minuto)

**En PowerShell:**
```powershell
# Intentar crear tarea como usuario normal (debe fallar)
$taskBody2 = @{
    title = "Intento de ataque"
    description = "El usuario normal intenta crear una tarea"
    assigned_to = $adminId
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8002/tasks/" -Method POST -Headers $userHeaders -Body $taskBody2
    Write-Host "❌ FALLO: El usuario no debería poder crear tareas"
} catch {
    Write-Host "✅ CORRECTO: Acceso denegado (403 Forbidden)"
    Write-Host "✅ Solo admins pueden crear tareas"
}
```

**Explicar:**
- Control de acceso basado en roles (RBAC)
- Autenticación con JWT
- Validación de roles en cada endpoint

---

### PASO 8: Ver Adminer - Bases de Datos (Bonus - 1 minuto)

**En navegador:**
```
http://localhost:8080
```

**Mostrar:**
- Sistema de gestión web para ver las bases de datos
- PostgreSQL con tabla de usuarios (auth_db)
- MySQL con tablas de tareas y notificaciones

---

## 📊 ARQUITECTURA MOSTRADA

```
┌─────────────────────────────────────────────────────────────┐
│                     DEMO CON DOCKER COMPOSE                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           CLIENTE (PowerShell en terminal)           │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼────────────────────────────────────┐   │
│  │          API GATEWAY (puerto 8000)                   │   │
│  │  ▪ Request routing                                   │   │
│  │  ▪ Load balancing                                    │   │
│  └──┬─────────────────┬───────────────────┬──────────────┘   │
│     │                 │                   │                  │
│  ┌──▼──────────────┐ ┌▼────────────────┐ ┌▼──────────────┐   │
│  │  AUTH SERVICE   │ │  TASK SERVICE   │ │NOTIFICATION   │   │
│  │  (puerto 8001)  │ │  (puerto 8002)  │ │(puerto 8003)  │   │
│  └──┬──────────────┘ └┬────────────────┘ └┬──────────────┘   │
│     │                 │                   │                  │
│  ┌──▼──────────────┐ ┌▼────────────────┐ │                  │
│  │    PostgreSQL   │ │     MySQL       ◄──┘                  │
│  │  (usuario auth) │ │  (tasks + notif)│                     │
│  └─────────────────┘ └─────────────────┘                     │
│                                                              │
│  + Redis (caché)                                            │
│  + Adminer (web UI para ver BD)                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ PUNTOS CLAVE A MENCIONAR

1. **Microservicios**: 3 servicios independientes
2. **Comunicación**: REST API + inter-servicios automáticos
3. **Bases de datos**: PostgreSQL (auth) + MySQL (tasks/notif)
4. **Seguridad**: JWT tokens + RBAC (admin vs user)
5. **Escalabilidad**: Docker permite escalar rápidamente
6. **Automatización**: Notificaciones generadas automáticamente

---

## 🔚 AL FINALIZAR LA DEMO

**Apagar servicios:**
```powershell
cd c:\Users\anyio\Desktop\TareasConNotificacion\PlataformadeTareasconNotificaciones\task-platform

docker-compose down
```

**Esto mantiene los datos en volúmenes (no los borra)**

---

---

---

# 🔵 OPCIÓN B: Demo con Kubernetes (ALTERNATIVA - si quieres mostrar orquestación)

## 📋 Preparación Previa (5-10 minutos antes de la clase)

### 1. Verificar que Docker Desktop esté corriendo
```powershell
docker --version
docker ps
```

### 2. Verificar que Kubernetes esté activo
```powershell
kubectl version --client
kubectl get nodes
```

### 2.5 (DESTACADO) Iniciar/recargar todos los pods
```powershell
# Ir a la carpeta de manifests
cd c:\Users\anyio\Desktop\TareasConNotificacion\PlataformadeTareasconNotificaciones\kubernetes

# Aplicar kustomize (crea/actualiza todos los recursos)
kubectl apply -k .

# Revisar estado
kubectl get pods -n task-platform
```

### 2.6 (DESTACADO) Reiniciar rápido si algo falla
```powershell
# Reiniciar todos los deployments
kubectl rollout restart deployment -n task-platform

# O reiniciar uno específico
kubectl rollout restart deployment/gateway -n task-platform
kubectl rollout restart deployment/task-service -n task-platform
kubectl rollout restart deployment/auth-service -n task-platform
kubectl rollout restart deployment/notification-service -n task-platform

# Revisar estado tras el restart
kubectl get pods -n task-platform
```

### 2.7 (DESTACADO) Apagar sin corromper datos
```powershell
# Detener workloads dejando datos intactos (PVCs se conservan)
kubectl scale deployment --all -n task-platform --replicas=0

# Confirmar que no quedan pods
kubectl get pods -n task-platform

# (Opcional) Limpiar objetos pero conservar datos (PVCs siguen vivos)
kubectl delete deployment --all -n task-platform
kubectl delete svc --all -n task-platform
kubectl delete ingress --all -n task-platform

# (Solo si deseas borrar TODO, incluidos datos) — no recomendado
# kubectl delete pvc --all -n task-platform
```

**Notas de apagado:**
- PVCs quedan intactos; solo borra `pvc` si quieres perder datos.
- Docker Desktop: basta con cerrar la app.
- Minikube: `minikube stop`. Kind: `kind delete cluster --name <nombre>`.


### 3. Verificar que los pods estén corriendo
```powershell
kubectl get pods -n task-platform
```

**Todos deben mostrar:** `1/1 Running`

Si hay pods con errores, reinicia:
```powershell
kubectl delete pod -n task-platform <nombre-del-pod>
```

---

## 🎬 DEMOSTRACIÓN EN CLASE (15-20 minutos)

### PARTE 1: Introducción y Arquitectura (3 minutos)

**Mostrar en pantalla:**

```powershell
# Ver todos los pods desplegados
kubectl get pods -n task-platform
```

**Explicar:**
- ✅ **3 microservicios independientes**: auth-service, task-service, notification-service
- ✅ **2 bases de datos**: PostgreSQL (auth), MySQL (tareas/notificaciones)
- ✅ **Gateway API**: punto de entrada unificado
- ✅ **Kubernetes**: orquestación con réplicas, health checks, escalabilidad

```powershell
# Ver los servicios de red
kubectl get services -n task-platform
```

```powershell
# Ver deployments con réplicas
kubectl get deployments -n task-platform
```

---

### PARTE 2: Arquitectura de Microservicios (5 minutos)

**Mostrar estructura del proyecto:**

```powershell
# Navegar al directorio
cd c:\Users\anyio\Desktop\TareasConNotificacion\PlataformadeTareasconNotificaciones

# Mostrar estructura
tree task-platform /F /A
```

**Explicar cada componente:**
- 📁 `auth-service/`: Autenticación con JWT, PostgreSQL
- 📁 `task-service/`: CRUD de tareas, MySQL
- 📁 `notification-service/`: Sistema de notificaciones, MySQL
- 📁 `gateway/`: API Gateway (punto único de entrada)
- 📁 `kubernetes/`: Manifiestos de despliegue

**Mostrar Dockerfiles optimizados:**
```powershell
cat task-platform\auth-service\Dockerfile
```

**Explicar:**
- Multi-stage builds (reducción 60% en tamaño)
- Imágenes base slim
- Non-root user (seguridad)

---

### PARTE 3: Despliegue en Kubernetes (3 minutos)

**Mostrar manifiestos:**

```powershell
# Listar archivos de Kubernetes
ls kubernetes\
```

**Explicar componentes:**
- `kustomization.yaml`: Gestión de configuración
- `namespace.yaml`: Aislamiento de recursos
- `configmaps.yaml`: Variables de entorno
- `secrets.yaml`: Credenciales (JWT, DB passwords)
- `databases.yaml`: PostgreSQL y MySQL con PVCs
- `deployments/`: Auth, Task, Notification, Gateway
- `services.yaml`: Networking interno
- `ingress.yaml`: Acceso externo

**Mostrar configuración aplicada:**
```powershell
kubectl get configmaps -n task-platform
kubectl get secrets -n task-platform
kubectl get pvc -n task-platform
```

---

### PARTE 4: Demostración Funcional (7 minutos)

#### 4.1 Port-Forward al Auth Service

**Terminal 1:**
```powershell
kubectl port-forward -n task-platform svc/auth-service 8001:8001
```

#### 4.2 Registrar Usuario Normal

**Terminal 2:**
```powershell
# Registrar usuario normal
$userResp = Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=demo1@example.com&password=demo123&role=user" -Method POST
$userResp | Format-List

# Guardar el token y ID
$userToken = $userResp.access_token
$userId = $userResp.id
Write-Host "✅ Usuario ID=$userId registrado con role=$($userResp.role)"
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyMiIsImVtYWlsIjoiZGVtbzFAZXhhbXBsZS5jb20iLCJyb2xlIjoidXNlci
               IsImV4cCI6MTc2NTE3NDk1OX0.ZjG77VC-_jCRynAqES6iFm-R_b_cEAcmjoUHf2Bs5cg
#### 4.3 Registrar Admin

**Terminal 2:**
```powershell
# Registrar usuario admin
$adminResp = Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=admin27@example.com&password=admin123&role=admin" -Method POST
$adminResp | Format-List

# Guardar el token y ID
$adminToken = $adminResp.access_token
$adminId = $adminResp.id
Write-Host "✅ Admin ID=$adminId registrado con role=$($adminResp.role)"
```

#### 4.4 Cambiar a Task Service

**Terminal 1 (Ctrl+C para detener el port-forward anterior):**
```powershell
kubectl port-forward -n task-platform svc/task-service 8002:8002
```

---

#### 4.5 Crear Tarea (con Admin)

**Terminal 2:**
```powershell
# Configurar headers con token admin
$adminHeaders = @{
    "Authorization" = "Bearer $adminToken"
    "Content-Type" = "application/json"
}

# Crear tarea asignada al usuario normal
$taskBody = @{
    title = "Demostración en clase"
    description = "Presentar arquitectura de microservicios"
    assigned_to = $userId
} | ConvertTo-Json

$taskResp = Invoke-RestMethod -Uri "http://localhost:8002/tasks/" -Method POST -Headers $adminHeaders -Body $taskBody
$taskResp | Format-List

$taskId = $taskResp.task_id
Write-Host "✅ Tarea ID=$taskId creada para usuario $userId"
Write-Host "✅ Notificación generada automáticamente"
```

**Explicar:**
- ✅ Solo admin (ID $adminId) puede crear tareas
- ✅ Tarea asignada a usuario normal (ID $userId)
- ✅ Se genera notificación automática

---

#### 4.6 Ver Tareas del Usuario

**Terminal 2:**
```powershell
# Configurar headers con token del usuario
$userHeaders = @{
    "Authorization" = "Bearer $userToken"
    "Content-Type" = "application/json"
}

# Ver tareas asignadas al usuario
$tasksResp = Invoke-RestMethod -Uri "http://localhost:8002/tasks/assigned" -Method GET -Headers $userHeaders
$tasksResp | Format-Table

Write-Host "✅ Usuario ID=$userId ve solo sus $($tasksResp.Count) tarea(s)"
```

**Explicar:**
- ✅ Usuario solo ve sus propias tareas
- ✅ No puede ver tareas de otros usuarios (user isolation)

---

#### 4.7 Ver Notificaciones

**Cambiar port-forward a notification-service:**

**Terminal 1:**
```powershell
kubectl port-forward -n task-platform svc/notification-service 8003:8003
```

**Terminal 2:**
```powershell
# Listar notificaciones del usuario
Invoke-RestMethod -Uri "http://localhost:8003/notifications/" -Method GET -Headers $userHeaders
```

**Mostrar:**
- Notificación automática generada al crear la tarea
- `is_read: false` (sin leer)
- `message`: Detalles de la tarea

---

### PARTE 5: Escalabilidad y Resiliencia (2 minutos)

```powershell
# Mostrar réplicas de cada servicio
kubectl get deployments -n task-platform
```

**Explicar:**
- Gateway: 3 réplicas (alta disponibilidad)
- Task-service: 3 réplicas (balanceo de carga)
- Auth-service: 2 réplicas
- Notification-service: 2 réplicas

**Simular fallo de un pod:**
```powershell
# Borrar un pod del task-service
kubectl delete pod -n task-platform <nombre-del-pod-task-service>

# Ver cómo Kubernetes lo recrea automáticamente
kubectl get pods -n task-platform -w
```

**Explicar:**
- ✅ Auto-healing: Kubernetes recrea pods automáticamente
- ✅ Rolling updates: Actualizaciones sin downtime
- ✅ Health checks: Liveness y Readiness probes

---

### PARTE 6: CI/CD y Docker Hub (2 minutos)

```powershell
# Mostrar GitHub Actions
cat .github\workflows\ci-cd.yml
```

**Explicar flujo CI/CD:**
1. Commit → GitHub Actions se activa
2. Build → Construye imágenes Docker
3. Test → Ejecuta pruebas (si existen)
4. Push → Sube imágenes a Docker Hub con tag
5. Deploy → Actualiza Kubernetes con nueva versión

**Mostrar imágenes en Docker Hub:**
- Abrir navegador: https://hub.docker.com/u/andreajos
- Mostrar repositorios:
  - `task-platform-auth-service:1.1.0`
  - `task-platform-task-service:1.1.0`
  - `task-platform-notification-service:1.1.0`
  - `task-platform-gateway:1.1.0`

---

## 📊 PUNTOS CLAVE PARA MENCIONAR

### ✅ Objetivos Cumplidos:

1. **Arquitectura de Microservicios**
   - División en servicios independientes
   - Cada servicio con responsabilidad única
   - Comunicación via REST API

2. **Dockerización**
   - Dockerfiles optimizados (multi-stage)
   - Imágenes en Docker Hub
   - Reducción 60% en tamaño de imágenes

3. **Kubernetes**
   - Manifiestos completos (Deployments, Services, ConfigMaps, Secrets)
   - Réplicas y escalabilidad
   - Health checks (liveness/readiness)
   - PersistentVolumeClaims para bases de datos
   - Auto-healing y rolling updates

4. **CI/CD**
   - GitHub Actions configurado
   - Build automático
   - Push a Docker Hub
   - Versionado de imágenes

5. **Seguridad**
   - JWT tokens para autenticación
   - Secrets de Kubernetes para credenciales
   - User isolation (cada usuario accede solo a sus datos)
   - Non-root containers

6. **Bases de Datos**
   - PostgreSQL para auth-service
   - MySQL para task-service y notification-service
   - Volúmenes persistentes

7. **Comunicación Inter-Servicios**
   - Task-service → Notification-service (automático)
   - JWT validation entre servicios

### ❌ No Implementado (mencionar si preguntan):

- **Service Mesh (Istio)**: No implementado
  - Requiere instalación adicional en el cluster
  - Opcional para proyectos de este tamaño
  
- **Ingeniería de Caos**: No implementado
  - Fuera del alcance del proyecto
  - Puede agregarse con Chaos Mesh o Litmus

- **Monitoreo Avanzado**: Básico
  - Logs en stdout/stderr (accesibles con `kubectl logs`)
  - Sin Prometheus/Grafana (puede agregarse)

---

## 🚨 Troubleshooting Durante la Demo

### Si un pod no arranca:
```powershell
kubectl describe pod -n task-platform <nombre-pod>
kubectl logs -n task-platform <nombre-pod>
```

### Si port-forward falla:
```powershell
# Verificar que no haya otro proceso usando el puerto
netstat -ano | findstr :8001

# Matar proceso si es necesario
taskkill /PID <PID> /F

# Reintentar port-forward
kubectl port-forward -n task-platform svc/auth-service 8001:8001
```

### Si la BD no responde:
```powershell
# Reiniciar pods de base de datos
kubectl delete pod -n task-platform <mysql-pod>
kubectl delete pod -n task-platform <postgres-pod>
```

### Si los tokens fallan:
- Asegurarse de copiar el token completo (sin espacios ni saltos de línea)
- Verificar que la variable `$headers` esté definida
- Regenerar token con nuevo login/register

---

## 🎓 PREGUNTAS FRECUENTES Y RESPUESTAS

**P: ¿Por qué no usar Istio?**
R: Istio agrega complejidad y overhead para un proyecto de este tamaño. Para 3 microservicios, la comunicación directa REST es suficiente. Istio se justifica en proyectos con 10+ servicios.

**P: ¿Cómo escala esto a producción?**
R: 
- Aumentar réplicas en deployments
- Configurar HPA (Horizontal Pod Autoscaler)
- Usar cluster managed (EKS, GKE, AKS)
- Agregar Ingress Controller (nginx, traefik)
- Implementar monitoreo (Prometheus + Grafana)

**P: ¿Qué pasa si MySQL falla?**
R: Los datos persisten en PVC. Al recrearse el pod, los datos se mantienen. Para alta disponibilidad en producción, usar MySQL replicado o RDS.

**P: ¿Cómo se hacen backups?**
R: 
- Snapshots de PVCs en Kubernetes
- Backups automáticos de bases de datos (mysqldump, pg_dump)
- Versionado en Git para código
- Imágenes versionadas en Docker Hub

---

## 🔚 CIERRE DE LA DEMOSTRACIÓN

**Resumir logros:**
- ✅ Arquitectura de microservicios funcional
- ✅ Desplegada en Kubernetes con alta disponibilidad
- ✅ CI/CD automatizado
- ✅ Seguridad con JWT
- ✅ Escalabilidad y auto-healing

**Limpiar recursos (opcional al final):**
```powershell
# Detener port-forwards (Ctrl+C en cada terminal)
# NO borrar el namespace si quieres mantener todo corriendo
```

---

## 📝 NOTAS FINALES

- Duración total: 15-20 minutos
- Tener terminal visible en pantalla grande
- Preparar tokens de antemano si hay problemas de red
- Tener backup de screenshots en caso de fallos
- Practicar la demo al menos una vez antes de la clase
