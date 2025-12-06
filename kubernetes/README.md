# Kubernetes Deployment - Task Platform

## 📋 Estructura

```
kubernetes/
├── namespace.yaml                    # Namespace task-platform
├── secrets-configmaps.yaml           # Secrets y ConfigMaps
├── databases.yaml                    # MySQL y PostgreSQL deployments
├── ingress.yaml                      # Ingress para acceso externo
├── kustomization.yaml                # Kustomize para deploy todo junto
├── deployments/
│   ├── auth-service.yaml             # Auth service deployment (2 replicas)
│   ├── task-service.yaml             # Task service deployment (3 replicas)
│   └── notification-service.yaml     # Notification service deployment (2 replicas)
└── services/
    └── backend-services.yaml         # ClusterIP services
```

## 🚀 Deployment Rápido

### Opción 1: Con Kustomize (RECOMENDADO)

```bash
# 1. Preparar credenciales en secrets-configmaps.yaml
nano kubernetes/secrets-configmaps.yaml
# Actualizar JWT_SECRET_KEY con valor seguro

# 2. Desplegar todo con un comando
kubectl apply -k kubernetes/

# 3. Verificar estado
kubectl get pods -n task-platform -w
kubectl get svc -n task-platform
```

### Opción 2: Manualmente (paso a paso)

```bash
# 1. Crear namespace
kubectl apply -f kubernetes/namespace.yaml

# 2. Crear secrets y configmaps
kubectl apply -f kubernetes/secrets-configmaps.yaml

# 3. Desplegar bases de datos
kubectl apply -f kubernetes/databases.yaml

# 4. Esperar que las BDs estén listas
kubectl wait --for=condition=ready pod -l app=mysql -n task-platform --timeout=300s
kubectl wait --for=condition=ready pod -l app=postgres -n task-platform --timeout=300s

# 5. Desplegar servicios
kubectl apply -f kubernetes/deployments/auth-service.yaml
kubectl apply -f kubernetes/deployments/task-service.yaml
kubectl apply -f kubernetes/deployments/notification-service.yaml

# 6. Crear services
kubectl apply -f kubernetes/services/backend-services.yaml

# 7. (Opcional) Crear Ingress
kubectl apply -f kubernetes/ingress.yaml
```

## ✅ Verificaciones

### Pods
```bash
kubectl get pods -n task-platform
# Esperado: 7 pods (2 auth + 3 task + 2 notification + 1 mysql + 1 postgres)

kubectl describe pod -n task-platform <pod-name>
# Ver eventos y logs

kubectl logs -n task-platform deployment/task-service
# Ver logs del servicio
```

### Services
```bash
kubectl get svc -n task-platform
# Ver services internos

kubectl get endpoints -n task-platform
# Ver endpoints (load balancing)
```

### Salud
```bash
# Health check desde dentro del cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://task-service.task-platform.svc.cluster.local:8002/health

# Esperado: {"status":"healthy","service":"task-service"}
```

## 🔗 Acceso a Servicios

### Dentro del cluster
```
http://auth-service:8001
http://task-service:8002
http://notification-service:8003
http://mysql:3306
http://postgres:5432
```

### Desde el host local (port-forward)
```bash
# Auth Service
kubectl port-forward -n task-platform svc/auth-service 8001:8001

# Task Service
kubectl port-forward -n task-platform svc/task-service 8002:8002

# Notification Service
kubectl port-forward -n task-platform svc/notification-service 8003:8003

# Luego acceder desde localhost:8001, localhost:8002, localhost:8003
curl http://localhost:8001/health
```

## 📊 Escalado

### Aumentar replicas
```bash
# Task Service (útil para aumentar capacidad)
kubectl scale deployment task-service --replicas=5 -n task-platform

# Verificar
kubectl get deployment -n task-platform
```

### Autoscaling (requiere Metrics Server)
```bash
# Crear HorizontalPodAutoscaler
kubectl autoscale deployment task-service \
  --min=3 --max=10 --cpu-percent=80 -n task-platform

# Ver HPA
kubectl get hpa -n task-platform
```

## 🔄 Actualizar Imágenes

### Nueva versión 1.1.0
```bash
# 1. Pushear nuevas imágenes a Docker Hub (con tag 1.1.0)
docker tag task-platform-auth-service:latest annyigs/task-platform-auth-service:1.1.0
docker push annyigs/task-platform-auth-service:1.1.0

# 2. Actualizar kustomization.yaml
nano kubernetes/kustomization.yaml
# Cambiar newTag: "1.1.0"

# 3. Hacer rollout
kubectl apply -k kubernetes/

# O manualmente:
kubectl set image deployment/auth-service \
  auth-service=annyigs/task-platform-auth-service:1.1.0 \
  -n task-platform

# 4. Ver progreso
kubectl rollout status deployment/auth-service -n task-platform
```

## 📝 Logs

```bash
# Todos los logs de un servicio
kubectl logs -n task-platform deployment/task-service --all-containers=true

# Seguimiento en tiempo real
kubectl logs -f -n task-platform deployment/task-service

# Último pod fallido
kubectl logs -n task-platform -p deployment/task-service

# Todos los pods de un label
kubectl logs -n task-platform -l app=task-service
```

## 🗑️ Limpiar

```bash
# Eliminar todo en el namespace
kubectl delete namespace task-platform

# O eliminar recursos específicamente
kubectl delete -k kubernetes/
```

## 🔐 Secretos

### Cambiar JWT_SECRET_KEY
```bash
# Opción 1: Actualizar el manifest
nano kubernetes/secrets-configmaps.yaml
# Cambiar JWT_SECRET_KEY
kubectl apply -f kubernetes/secrets-configmaps.yaml

# Opción 2: Crear secret manualmente
kubectl create secret generic jwt-secrets \
  --from-literal=JWT_SECRET_KEY="new-secret-key" \
  -n task-platform \
  --dry-run=client -o yaml | kubectl apply -f -

# Los pods necesitarán ser reiniciados para usar el nuevo secret:
kubectl rollout restart deployment/auth-service -n task-platform
kubectl rollout restart deployment/task-service -n task-platform
kubectl rollout restart deployment/notification-service -n task-platform
```

## 🧪 Test E2E en Kubernetes

### 1. Port-forward
```bash
kubectl port-forward svc/auth-service 8001:8001 -n task-platform &
kubectl port-forward svc/task-service 8002:8002 -n task-platform &
kubectl port-forward svc/notification-service 8003:8003 -n task-platform &
```

### 2. Registrar usuario
```bash
curl -X POST "http://localhost:8001/auth/register?email=k8s@test.com&password=secure123"
# Obtener JWT token
```

### 3. Crear tarea
```bash
TOKEN="<jwt-token-from-register>"
curl -X POST http://localhost:8002/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"K8s Test","description":"Testing in Kubernetes","assigned_to":1}'
```

### 4. Ver notificaciones
```bash
curl http://localhost:8003/notifications \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Monitorización

### Prometheus (opcional)
```bash
# Agregar ServiceMonitor para Prometheus
# Requiere Prometheus Operator instalado
kubectl apply -f kubernetes/prometheus-servicemonitor.yaml
```

### Logs centralizados (opcional)
```bash
# Si tienes ELK Stack o Loki instalado
# Los logs van automáticamente a stdout/stderr
# Compatible con Fluent Bit, Logstash, Promtail
```

## 🎯 Troubleshooting

### Pod no inicia
```bash
kubectl describe pod -n task-platform <pod-name>
kubectl logs -n task-platform <pod-name>
```

### Service discovery falla
```bash
# Verificar DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup task-service.task-platform.svc.cluster.local
```

### Base de datos no responde
```bash
kubectl exec -it -n task-platform deployment/mysql -- mysql -u root -padmin123
```

---

**Estado:** ✅ Manifests listos para deploy en Kubernetes

**Próximo:** Pushear imágenes a Docker Hub, luego hacer `kubectl apply -k kubernetes/`

