# 🎯 GUÍA DE DEMOSTRACIÓN - PLATAFORMA DE TAREAS CON NOTIFICACIONES

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

#### 4.2 Registrar Usuario

**Terminal 2:**
```powershell
# Registrar usuario normal
Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=demo@example.com&password=demo123&role=user" -Method POST
```

**Mostrar respuesta:**
- `access_token`: JWT generado
- `user_id`: ID del usuario
- `role`: Rol asignado

**Guardar el token:**
```powershell
$userToken = "COPIAR_TOKEN_AQUI"
```

#### 4.3 Registrar Admin

```powershell
# Registrar usuario admin
Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=admin@example.com&password=admin123&role=admin" -Method POST
```

**Guardar el token admin:**
```powershell
$adminToken = "COPIAR_TOKEN_ADMIN_AQUI"
```

#### 4.4 Login

```powershell
# Probar login
Invoke-RestMethod -Uri "http://localhost:8001/auth/login?email=demo@example.com&password=demo123" -Method POST
```

---

#### 4.5 Crear Tarea

**Cambiar port-forward a task-service (Ctrl+C en Terminal 1):**

**Terminal 1:**
```powershell
kubectl port-forward -n task-platform svc/task-service 8002:8002
```

**Terminal 2:**
```powershell
# Configurar headers
$adminToken = "TOKEN_ADMIN_AQUI"
$headers = @{
    "Authorization" = "Bearer $adminToken"
    "Content-Type" = "application/json"
}

# Crear tarea
$body = @{
    title = "Demostración en clase"
    description = "Presentar arquitectura de microservicios"
    assigned_to = 1  # ID del usuario demo
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8002/tasks/" -Method POST -Headers $headers -Body $body
```

**Explicar:**
- ✅ Solo admins pueden crear tareas
- ✅ Tarea asignada al usuario con ID 1
- ✅ Automáticamente se genera una notificación

---

#### 4.6 Ver Tareas Asignadas

```powershell
# Usar token del usuario (no admin)
$userToken = "TOKEN_USUARIO_AQUI"
$userHeaders = @{
    "Authorization" = "Bearer $userToken"
    "Content-Type" = "application/json"
}

# Listar tareas asignadas
Invoke-RestMethod -Uri "http://localhost:8002/tasks/assigned" -Method GET -Headers $userHeaders
```

**Explicar:**
- ✅ Cada usuario solo ve sus tareas
- ✅ Aislamiento de datos por usuario (user isolation)

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