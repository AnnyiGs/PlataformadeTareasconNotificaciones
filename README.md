# 📋 Plataforma de Tareas con Notificaciones

Una **arquitectura de microservicios moderna** diseñada para gestionar tareas y notificaciones en tiempo real. Deployada en **Kubernetes** con alta disponibilidad, escalabilidad automática y CI/CD completamente automatizado.

---

## 🎯 ¿Qué es este proyecto?

Una plataforma completa de gestión de tareas que demuestra las mejores prácticas en:
- 🏗️ **Arquitectura de microservicios** con responsabilidad única
- 🐳 **Containerización con Docker** (imágenes optimizadas)
- ☸️ **Orquestación con Kubernetes** (réplicas, auto-healing, escalabilidad)
- 🔐 **Autenticación JWT** con roles y aislamiento de datos
- 🔄 **CI/CD automatizado** (GitHub Actions → Docker Hub → Kubernetes)
- 📊 **Bases de datos independientes** (PostgreSQL + MySQL)

---

## 🏛️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (3 réplicas)               │
│                    (Puerto: 8000)                            │
└─────────────┬───────────────────────────────────────────────┘
              │
    ┌─────────┼─────────┬─────────────┐
    │         │         │             │
    ▼         ▼         ▼             ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌────────────┐
│ Auth   │ │ Task   │ │Notif.    │ │Databases   │
│Service │ │Service │ │Service   │ │            │
│(2 rep) │ │(3 rep) │ │(2 rep)   │ │PostgreSQL  │
└────────┘ └────────┘ └──────────┘ │  + MySQL   │
   ▲         ▲         ▲            │            │
   │         │         │            └────────────┘
   └─────────┴─────────┘
   JWT Token Validation
   & Inter-Service Calls
```

### 🔧 Componentes

| Servicio | Puerto | BD | Réplicas | Responsabilidad |
|----------|--------|-------|----------|-----------------|
| **Gateway** | 8000 | - | 3 | Punto único de entrada, enrutamiento |
| **Auth Service** | 8001 | PostgreSQL | 2 | Autenticación, JWT, gestión de usuarios |
| **Task Service** | 8002 | MySQL | 3 | CRUD de tareas, asignaciones |
| **Notification Service** | 8003 | MySQL | 2 | Notificaciones automáticas |

---

## ✨ Características Principales

### 🔐 Seguridad
- Autenticación JWT con tokens de 8 horas
- Roles (usuario, admin) con control de acceso
- Aislamiento de datos por usuario
- Secrets de Kubernetes para credenciales
- Contenedores non-root

### ⚡ Escalabilidad
- **Auto-scaling**: Réplicas por servicio
- **Load balancing**: Distribución automática
- **Health checks**: Liveness y readiness probes
- **Auto-healing**: Reconstrucción de pods fallidos
- **Rolling updates**: Despliegues sin downtime

### 📦 DevOps
- **Dockerización**: Multi-stage builds (60% reducción de tamaño)
- **CI/CD**: GitHub Actions → Docker Hub → Kubernetes
- **Versionado**: Imágenes semánticas (1.1.0)
- **Manifiestos**: Kubernetes con kustomize

### 💾 Datos
- **Persistencia**: PersistentVolumeClaims (5Gi por BD)
- **Bases separadas**: PostgreSQL (auth) + MySQL (tareas/notificaciones)
- **Aislamiento**: Cada servicio accede solo a su BD

---

## 🚀 Inicio Rápido

### Requisitos Previos
```powershell
# Verificar instalaciones
docker --version          # Docker Desktop
kubectl version --client  # Kubernetes
```

### 1️⃣ Desplegar en Kubernetes
```powershell
cd kubernetes
kubectl apply -k .
```

### 2️⃣ Verificar que los servicios estén corriendo
```powershell
kubectl get pods -n task-platform
# Todos deben mostrar: 1/1 Running
```

### 3️⃣ Acceder a los servicios (port-forward)
```powershell
# Terminal 1 - Auth Service
kubectl port-forward -n task-platform svc/auth-service 8001:8001

# Terminal 2 - Task Service
kubectl port-forward -n task-platform svc/task-service 8002:8002

# Terminal 3 - Notification Service
kubectl port-forward -n task-platform svc/notification-service 8003:8003
```

### 4️⃣ Ejemplo: Registrar usuario
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=demo@example.com&password=demo123&role=user" -Method POST
```

---

## 📚 Documentación Completa

| Documento | Descripción | Cuándo Usarlo |
|-----------|-------------|---------------|
| **[GUIA_DEMOSTRACION.md](./GUIA_DEMOSTRACION.md)** | Paso a paso para demostración en clase (15-20 min) | Antes de presentar el proyecto |
| **[doc.txt](./doc.txt)** | Resumen de requisitos implementados y pendientes | Para validar completitud |
| **[README.md](./README.md)** | Este archivo - visión general del proyecto | Introducción rápida |

### 📖 Lectura Recomendada
1. **Primero**: Este README (5 min)
2. **Luego**: `doc.txt` para ver requisitos (5 min)
3. **Finalmente**: `GUIA_DEMOSTRACION.md` para ejecutar (20 min)

---

## 🎬 Demo en Vivo

Para una demostración completa de 15-20 minutos que incluye:
- Arquitectura y componentes
- Autenticación con JWT
- Creación de tareas
- Generación automática de notificaciones
- Escalabilidad y resiliencia

👉 **Ver**: [GUIA_DEMOSTRACION.md](./GUIA_DEMOSTRACION.md)

---

## 📊 Estado del Proyecto

|     Aspecto    |     Estado  |                         Detalles                         |
|----------------|-------------|----------------------------------------------------------|
| Microservicios |    Completo | Auth, Task, Notification, Gateway                        |
| Kubernetes     |    Completo | Deployments, Services, ConfigMaps, Secrets, PVCs         |
| CI/CD          |    Completo | GitHub Actions → Docker Hub                              |
| Autenticación  |    Completo | JWT con roles y user isolation                           |
| Escalabilidad  |    Completo | Réplicas, health checks, auto-healing                    |
| Persistencia   |    Completo | PostgreSQL + MySQL con PVCs                              |

**Completitud**: 85% (17/20 requisitos académicos implementados requeridos para el sistema)

Para más detalles → [doc.txt](./doc.txt)

---

## 🛠️ Estructura del Proyecto

```
PlataformadeTareasconNotificaciones/
├── README.md                          # Este archivo
├── doc.txt                            # Requisitos y estado
├── GUIA_DEMOSTRACION.md              # Demo paso a paso
├── task-platform/
│   ├── auth-service/                 # Autenticación (JWT, PostgreSQL)
│   ├── task-service/                 # Gestión de tareas (MySQL)
│   ├── notification-service/         # Notificaciones (MySQL)
│   ├── gateway/                      # API Gateway (enrutamiento)
│   └── docker-compose.yml            # Alternativa: desarrollo local
├── kubernetes/                        # Manifiestos K8s
│   ├── kustomization.yaml            # Base de configuración
│   ├── namespace.yaml                # Aislamiento
│   ├── configmaps.yaml               # Variables de entorno
│   ├── secrets.yaml                  # Credenciales
│   ├── databases.yaml                # PostgreSQL + MySQL
│   └── deployments/                  # Servicios
└── .github/
    └── workflows/
        └── ci-cd.yml                 # GitHub Actions
```

---

## 🔄 Flujo CI/CD

```
1. Push a GitHub
    ↓
2. GitHub Actions activa
    ↓
3. Build de imágenes Docker
    ↓
4. Push a Docker Hub (andreajos/...)
    ↓
5. Actualización automática en Kubernetes
    ↓
6. Rolling update sin downtime
```

---

## 🛑 Apagar Correctamente

Cuando termines de trabajar, apaga sin perder datos:

```powershell
# Escalar a 0 (pausa sin borrar nada)
kubectl scale deployment --all -n task-platform --replicas=0

# (Opcional) Limpiar objetos pero conservar datos
kubectl delete deployment --all -n task-platform
kubectl delete svc --all -n task-platform
kubectl delete ingress --all -n task-platform

# Cierra Docker Desktop / Minikube / Kind
# LOS DATOS PERSISTEN EN PVCs
```

👉 Para más detalles: [GUIA_DEMOSTRACION.md - Sección 2.7](./GUIA_DEMOSTRACION.md#27-destacado-apagar-sin-corromper-datos)

---

## 🎓 Propósitos Educativos

Este proyecto es ideal para aprender:
- ✅ Diseño de microservicios
- ✅ Containerización con Docker
- ✅ Orquestación con Kubernetes
- ✅ Autenticación y seguridad (JWT)
- ✅ CI/CD con GitHub Actions
- ✅ Persistencia de datos
- ✅ Escalabilidad y resiliencia

---

## 📝 Notas Importantes

- **Sin service mesh**: Istio no está implementado (no necesario para 3 microservicios)
- **Monitoreo básico**: Logs con `kubectl logs` (Prometheus/Grafana opcional)
- **Bases de datos en cluster**: Para producción, usar RDS/Cloud SQL
- **Datos seguros**: PVCs persisten incluso tras borrar deployments

---

## 🔗 Recursos Adicionales

- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Docker Hub - Imágenes del proyecto](https://hub.docker.com/u/andreajos)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

## 📧 Autor

**Andrea Ortega**  
Proyecto académico de arquitectura de microservicios

---

<div align="center">

**¿Listo para la demo?** → [Ver GUIA_DEMOSTRACION.md](./GUIA_DEMOSTRACION.md)

**Validar requisitos** → [Ver doc.txt](./doc.txt)

</div>