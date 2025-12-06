# Pre-Kubernetes Checklist & Roadmap

## 🎯 Estado Actual: Mejoras Implementadas ✅

### Fase 1: Kubernetes Readiness (COMPLETADO ✅)

- [x] Health check endpoints (`GET /health`)
- [x] Variables de ambiente configurables
- [x] Dockerfiles optimizados (multi-stage)
- [x] Logging estructurado
- [x] HEALTHCHECK en Dockerfiles
- [x] Eventos de startup logging
- [x] Compatibilidad Docker Compose ↔ K8s
- [x] Todas las verificaciones pasadas
- [x] Documentación completa

**Resultado:** Imágenes listas para Kubernetes

---

## 📋 Fases Siguientes (Ordenadas por Prioridad)

### Fase 2: Docker Hub (1-2 horas) ⏳ PRÓXIMO

**Tareas:**
- [ ] Crear cuenta en Docker Hub (si no existe)
- [ ] Crear 3 repositorios públicos:
  - [ ] `task-platform-auth-service`
  - [ ] `task-platform-task-service`
  - [ ] `task-platform-notification-service`
- [ ] Hacer login: `docker login`
- [ ] Etiquetar imágenes locales:
  ```powershell
  docker tag task-platform-auth-service:latest annyigs/task-platform-auth-service:latest
  docker tag task-platform-task-service:latest annyigs/task-platform-task-service:latest
  docker tag task-platform-notification-service:latest annyigs/task-platform-notification-service:latest
  ```
- [ ] Pushear a Docker Hub:
  ```powershell
  docker push annyigs/task-platform-auth-service:latest
  docker push annyigs/task-platform-task-service:latest
  docker push annyigs/task-platform-notification-service:latest
  ```
- [ ] Verificar en https://hub.docker.com/u/annyigs

**Entregable:** Imágenes disponibles en Docker Hub
**Documentación:** [DOCKER_HUB_GUIDE.md](./DOCKER_HUB_GUIDE.md)

---

### Fase 3: Kubernetes Manifests (4-6 horas)

**Estructura de directorios:**
```
kubernetes/
├── namespace.yaml          # Namespace para la aplicación
├── secrets.yaml           # JWT_SECRET_KEY, DB credentials
├── configmaps.yaml        # Variables de ambiente generales
├── deployments/
│   ├── auth-service.yaml
│   ├── task-service.yaml
│   └── notification-service.yaml
├── services/
│   ├── auth-service.yaml
│   ├── task-service.yaml
│   └── notification-service.yaml
├── databases/
│   ├── mysql-deployment.yaml
│   ├── mysql-service.yaml
│   ├── postgres-deployment.yaml
│   └── postgres-service.yaml
├── ingress.yaml           # Para acceso externo
└── README.md
```

**Tareas:**
- [ ] Crear `kubernetes/namespace.yaml`
- [ ] Crear `kubernetes/secrets.yaml` con:
  - [ ] `JWT_SECRET_KEY`
  - [ ] `MYSQL_ROOT_PASSWORD`
  - [ ] `POSTGRES_PASSWORD`
- [ ] Crear `kubernetes/configmaps.yaml` con:
  - [ ] URLs de servicios
  - [ ] Variables de database
- [ ] Crear deployments para 3 servicios:
  - [ ] auth-service (1 replica, requests: 256Mi memory)
  - [ ] task-service (2 replicas, requests: 256Mi memory)
  - [ ] notification-service (2 replicas, requests: 256Mi memory)
- [ ] Crear services ClusterIP para cada uno
- [ ] Crear deployments para MySQL y PostgreSQL
- [ ] Crear PersistentVolumeClaims para bases de datos
- [ ] Crear Ingress para acceso externo

**Verificaciones:**
```bash
kubectl apply -f kubernetes/
kubectl get pods -w                    # Esperar que todos estén Running
kubectl get svc                        # Ver servicios
kubectl logs deployment/task-service   # Ver logs
kubectl port-forward svc/task-service 8002:8002
curl http://localhost:8002/health      # Debe retornar {"status":"healthy"}
```

**Entregable:** Stack Kubernetes funcional
**Documentación:** [KUBERNETES_READINESS.md](./task-platform/KUBERNETES_READINESS.md)

---

### Fase 4: Verificar Comunicación Inter-Servicios en K8s (2 horas)

**Objetivo:** Confirmar que task-service puede llamar a notification-service dentro del cluster

**Pasos:**
1. [ ] Deploy ambos servicios en Kubernetes
2. [ ] Ejecutar comando dentro del pod de task-service:
   ```bash
   kubectl exec -it deployment/task-service -- /bin/bash
   curl http://notification-service:8003/health
   # Debe responder: {"status":"healthy","service":"notification-service"}
   ```
3. [ ] Crear una tarea desde fuera:
   ```bash
   curl -X POST http://localhost:8002/tasks/ \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"title":"K8s Test","description":"...","assigned_to":1}'
   ```
4. [ ] Verificar que la notificación se creó:
   ```bash
   curl http://localhost:8003/notifications \
     -H "Authorization: Bearer <token>"
   # Debe retornar la notificación creada
   ```
5. [ ] Revisar logs del pod de task-service:
   ```bash
   kubectl logs deployment/task-service
   # Debe mostrar: "INFO:routers.tasks:Notification sent for task <id>"
   ```

**Entregable:** Confirmación de comunicación inter-servicios en K8s
**Éxito:** Task-service puede enviar notificaciones a notification-service sin pasar por localhost

---

### Fase 5: GitHub Actions CI/CD (3-4 horas) [OPCIONAL PERO RECOMENDADO]

**Objetivo:** Automatizar build y push a Docker Hub

**Tareas:**
- [ ] Crear `.github/workflows/docker-push.yml`
- [ ] Configurar secretos en GitHub:
  - [ ] `DOCKER_USERNAME`
  - [ ] `DOCKER_PASSWORD` (token, no contraseña)
- [ ] Workflow debe:
  - [ ] Buildear en cada push a `main`
  - [ ] Tagear con `latest` y SHA de commit
  - [ ] Pushear a Docker Hub
  - [ ] Ejecutar tests (si existen)

**Entregable:** CI/CD pipeline automático
**Documentación:** Incluida en DOCKER_HUB_GUIDE.md

---

### Fase 6: Prometheus + Grafana (4-8 horas) [OPCIONAL]

**Objetivo:** Monitorización y observabilidad

**Tareas:**
- [ ] Agregar biblioteca `prometheus-client` a requirements.txt
- [ ] Crear endpoint `/metrics` en cada servicio
- [ ] Desplegar Prometheus en K8s
- [ ] Desplegar Grafana en K8s
- [ ] Configurar Grafana para usar Prometheus como datasource
- [ ] Crear dashboards:
  - [ ] Tasa de requests
  - [ ] Latencia (p95, p99)
  - [ ] Errores por servicio
  - [ ] Uso de CPU/Memoria

**Entregable:** Dashboards de observabilidad en tiempo real

---

## 📊 Timeline Estimado

| Fase | Descripción | Horas | Acumulado |
|------|-------------|-------|-----------|
| 1 (✅) | Kubernetes Readiness | 3-4 | 3-4h |
| 2 | Docker Hub | 1-2 | 4-6h |
| 3 | Kubernetes Manifests | 4-6 | 8-12h |
| 4 | Verificar Inter-servicios | 2 | 10-14h |
| 5 (opt) | GitHub Actions CI/CD | 3-4 | 13-18h |
| 6 (opt) | Prometheus + Grafana | 4-8 | 17-26h |

**Mínimo para Kubernetes:** 10-14 horas (fases 1-4)
**Con CI/CD:** 13-18 horas
**Completo (con observabilidad):** 17-26 horas

---

## 🚀 Quick Start: Próximos 2 Días

### Día 1 (4 horas)
- [ ] Completar Fase 2 (Docker Hub)
- [ ] Empezar Fase 3 (Kubernetes Manifests)

### Día 2 (6 horas)
- [ ] Completar Fase 3 (Kubernetes Manifests)
- [ ] Completar Fase 4 (Verificar comunicación)
- [ ] (Opcional) Empezar Fase 5 (CI/CD)

**Resultado:** Stack Kubernetes funcional con comunicación inter-servicios verificada

---

## 🔍 Validaciones Finales

### Antes de pasar a Kubernetes:
- [ ] Todos los health checks responden
- [ ] End-to-end flow funciona en Docker Compose
- [ ] Logs son claros y estructurados
- [ ] Imágenes son optimizadas (<100MB cada una)
- [ ] Variables de ambiente son configurables

### En Kubernetes:
- [ ] Pods inician correctamente
- [ ] Services se pueden descubrir entre sí
- [ ] Requests entre servicios funcionan
- [ ] Logs aparecen en kubectl logs
- [ ] Health probes detectan salud

---

## 📝 Notas Importantes

### Sobre Docker Hub
- Username público es visible (ej: `annyigs`)
- Las imágenes deben ser **Public** para que otros las descarguen
- Usar token de acceso (no contraseña) para seguridad

### Sobre Kubernetes
- Requiere un cluster (minikube local, o EKS/GKE en cloud)
- Los recursos por pod deben especificarse (CPU/Memory requests)
- Las bases de datos en K8s son complejas; considerar cloud-managed (RDS, Cloud SQL)

### Sobre CI/CD
- Opcional pero muy recomendado para producción
- Requiere secrets configurados en GitHub
- Automatizan builds y deploys

---

## ✅ Checklist Final

**Antes de Kubernetes:**
- [x] Mejoras implementadas
- [x] Tests pasados
- [x] Documentación completa
- [ ] Imágenes en Docker Hub
- [ ] Manifests Kubernetes creados
- [ ] Deploy verificado en K8s
- [ ] Comunicación inter-servicios en K8s confirmada

**Después de Kubernetes:**
- [ ] (Opcional) CI/CD automático
- [ ] (Opcional) Observabilidad con Prometheus
- [ ] (Opcional) RBAC Kubernetes
- [ ] (Opcional) Secrets management avanzado

---

## 📞 Próximos Pasos

**Mensaje para continuar:**
"Adelante con Fase 2: Docker Hub"

**O si prefieres saltarte Docker Hub:**
"Crear Kubernetes manifests directamente" (requiere builds locales)

---

**Creado:** Diciembre 5, 2025  
**Estado:** ✅ Listo para pasar a Kubernetes  
**Siguiente:** Docker Hub o Kubernetes Manifests

