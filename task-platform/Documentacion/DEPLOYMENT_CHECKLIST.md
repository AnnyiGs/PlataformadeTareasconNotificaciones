# ✅ Kubernetes Deployment Checklist

## Pre-Requisitos

- [ ] Cluster Kubernetes disponible (minikube, EKS, GKE, o local)
- [ ] `kubectl` instalado y configurado
- [ ] Docker Hub cuenta creada (para pushear imágenes)
- [ ] Imágenes tageadas correctamente (annyigs/...)

## Fase 2: Docker Hub (1-2 horas)

### Pasos:

- [ ] **2.1 - Etiquetar imágenes locales**
  ```bash
  docker tag task-platform-auth-service:latest annyigs/task-platform-auth-service:1.0.0
  docker tag task-platform-task-service:latest annyigs/task-platform-task-service:1.0.0
  docker tag task-platform-notification-service:latest annyigs/task-platform-notification-service:1.0.0
  ```

- [ ] **2.2 - Verificar etiquetado**
  ```bash
  docker images | grep annyigs
  ```

- [ ] **2.3 - Login a Docker Hub**
  ```bash
  docker login
  # Usar credenciales de Docker Hub
  ```

- [ ] **2.4 - Pushear imágenes**
  ```bash
  docker push annyigs/task-platform-auth-service:1.0.0
  docker push annyigs/task-platform-task-service:1.0.0
  docker push annyigs/task-platform-notification-service:1.0.0
  ```

- [ ] **2.5 - Verificar en Docker Hub**
  - Ir a https://hub.docker.com/u/annyigs
  - Confirmar que 3 repositorios existen
  - Confirmar que tags 1.0.0 están disponibles

### Resultado esperado:
✅ Imágenes disponibles en Docker Hub (públicas)

---

## Fase 3: Kubernetes Manifests (4-6 horas)

### Archivos creados:

- [x] `kubernetes/namespace.yaml` - Namespace task-platform
- [x] `kubernetes/secrets-configmaps.yaml` - Secrets + ConfigMaps
- [x] `kubernetes/databases.yaml` - MySQL + PostgreSQL
- [x] `kubernetes/deployments/auth-service.yaml` - Auth deployment
- [x] `kubernetes/deployments/task-service.yaml` - Task deployment
- [x] `kubernetes/deployments/notification-service.yaml` - Notification deployment
- [x] `kubernetes/services/backend-services.yaml` - ClusterIP services
- [x] `kubernetes/ingress.yaml` - Ingress (opcional)
- [x] `kubernetes/kustomization.yaml` - Kustomize manifest
- [x] `kubernetes/README.md` - Documentación

### Validación de manifests:

- [ ] **3.1 - Validar sintaxis YAML**
  ```bash
  kubectl apply -k kubernetes/ --dry-run=client
  # Esperado: (no errors)
  ```

- [ ] **3.2 - Revisar manifests generados**
  ```bash
  kubectl kustomize kubernetes/ | less
  # Revisar que las imágenes, variables de env, secrets, etc. estén correctos
  ```

### Resultado esperado:
✅ Manifests YAML válidos listos para deploy

---

## Fase 4: Deploy en Kubernetes (2+ horas)

### Pre-deploy:

- [ ] **4.1 - Asegurar cluster está disponible**
  ```bash
  kubectl cluster-info
  # Esperado: ver API server URL
  ```

- [ ] **4.2 - Crear namespace**
  ```bash
  kubectl create namespace task-platform
  # O con manifest: kubectl apply -f kubernetes/namespace.yaml
  ```

- [ ] **4.3 - Actualizar secretos (IMPORTANTE)**
  ```bash
  # Editar kubernetes/secrets-configmaps.yaml
  nano kubernetes/secrets-configmaps.yaml
  
  # Cambiar JWT_SECRET_KEY a valor seguro
  # Cambiar MYSQL_ROOT_PASSWORD y POSTGRES_PASSWORD si es necesario
  ```

### Deploy:

- [ ] **4.4 - Deploy bases de datos PRIMERO**
  ```bash
  kubectl apply -f kubernetes/namespace.yaml
  kubectl apply -f kubernetes/secrets-configmaps.yaml
  kubectl apply -f kubernetes/databases.yaml
  ```

- [ ] **4.5 - Esperar a que MySQL y PostgreSQL estén listas**
  ```bash
  kubectl wait --for=condition=ready pod -l app=mysql -n task-platform --timeout=300s
  kubectl wait --for=condition=ready pod -l app=postgres -n task-platform --timeout=300s
  
  # Verificar manualmente:
  kubectl get pods -n task-platform
  # Esperado: mysql-xxx y postgres-xxx con STATUS Running
  ```

- [ ] **4.6 - Deploy servicios backend**
  ```bash
  kubectl apply -f kubernetes/deployments/auth-service.yaml
  kubectl apply -f kubernetes/deployments/task-service.yaml
  kubectl apply -f kubernetes/deployments/notification-service.yaml
  ```

- [ ] **4.7 - Esperar a que servicios estén listos**
  ```bash
  kubectl wait --for=condition=ready pod -l app=auth-service -n task-platform --timeout=300s
  kubectl wait --for=condition=ready pod -l app=task-service -n task-platform --timeout=300s
  kubectl wait --for=condition=ready pod -l app=notification-service -n task-platform --timeout=300s
  
  # Verificar manualmente:
  kubectl get pods -n task-platform
  # Esperado: 7 pods todos con STATUS Running
  ```

- [ ] **4.8 - Crear services**
  ```bash
  kubectl apply -f kubernetes/services/backend-services.yaml
  ```

- [ ] **4.9 - (Opcional) Crear Ingress**
  ```bash
  # Solo si tienes Ingress controller instalado (nginx-ingress, etc)
  kubectl apply -f kubernetes/ingress.yaml
  ```

### Resultado esperado:
✅ 7 pods running (2 auth + 3 task + 2 notification + 1 mysql + 1 postgres)

---

## Fase 5: Verificación en Kubernetes (1-2 horas)

### Estado de pods:

- [ ] **5.1 - Ver todos los pods**
  ```bash
  kubectl get pods -n task-platform
  ```

- [ ] **5.2 - Ver logs de inicialización**
  ```bash
  kubectl logs -n task-platform deployment/auth-service
  # Esperado: ver "Auth Service started"
  ```

- [ ] **5.3 - Ver descripción de pod fallido (si existe)**
  ```bash
  kubectl describe pod -n task-platform <pod-name>
  # Ver eventos y errores
  ```

### Network y servicios:

- [ ] **5.4 - Ver services**
  ```bash
  kubectl get svc -n task-platform
  # Esperado: auth-service, task-service, notification-service con IP interna
  ```

- [ ] **5.5 - Ver endpoints**
  ```bash
  kubectl get endpoints -n task-platform
  # Esperado: cada servicio con 2-3 IPs (pods)
  ```

### Health checks:

- [ ] **5.6 - Port-forward a auth-service**
  ```bash
  kubectl port-forward svc/auth-service 8001:8001 -n task-platform
  # En otra terminal:
  curl http://localhost:8001/health
  # Esperado: {"status":"healthy","service":"auth-service"}
  ```

- [ ] **5.7 - Port-forward a task-service**
  ```bash
  kubectl port-forward svc/task-service 8002:8002 -n task-platform
  curl http://localhost:8002/health
  # Esperado: {"status":"healthy","service":"task-service"}
  ```

- [ ] **5.8 - Port-forward a notification-service**
  ```bash
  kubectl port-forward svc/notification-service 8003:8003 -n task-platform
  curl http://localhost:8003/health
  # Esperado: {"status":"healthy","service":"notification-service"}
  ```

### Resultado esperado:
✅ Health checks todos retornan 200 OK

---

## Fase 6: End-to-End Test en Kubernetes (1-2 horas)

### Setup port-forward:

- [ ] **6.1 - Abrir 3 terminales para port-forward**
  ```bash
  # Terminal 1:
  kubectl port-forward svc/auth-service 8001:8001 -n task-platform

  # Terminal 2:
  kubectl port-forward svc/task-service 8002:8002 -n task-platform

  # Terminal 3:
  kubectl port-forward svc/notification-service 8003:8003 -n task-platform
  ```

### Test flow:

- [ ] **6.2 - Registrar usuario**
  ```bash
  curl -X POST "http://localhost:8001/auth/register?email=k8s@test.com&password=secure123"
  # Guardar JWT token
  TOKEN="eyJ..."
  ```

- [ ] **6.3 - Crear tarea**
  ```bash
  curl -X POST http://localhost:8002/tasks/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title":"K8s Test","description":"Testing in Kubernetes","assigned_to":1}'
  # Esperado: task creada con ID
  ```

- [ ] **6.4 - Listar notificaciones**
  ```bash
  curl http://localhost:8003/notifications \
    -H "Authorization: Bearer $TOKEN"
  # Esperado: notificación de "Nueva tarea asignada"
  ```

- [ ] **6.5 - Ver logs de task-service**
  ```bash
  kubectl logs -n task-platform deployment/task-service
  # Esperado: ver "Notification sent for task X"
  ```

### Resultado esperado:
✅ End-to-end flow completo funciona en Kubernetes

---

## Fase 7: Verificación Inter-Servicios (1 hora)

### Comunicación desde pod:

- [ ] **7.1 - Conectarse a pod de task-service**
  ```bash
  kubectl exec -it deployment/task-service -n task-platform -- /bin/bash
  ```

- [ ] **7.2 - Hacer curl desde adentro del pod**
  ```bash
  # Dentro del pod:
  curl http://notification-service:8003/health
  # Esperado: {"status":"healthy","service":"notification-service"}
  ```

- [ ] **7.3 - Verificar DNS resolution**
  ```bash
  # Dentro del pod:
  nslookup notification-service
  # Esperado: resolver correctamente a IP interna
  ```

### Resultado esperado:
✅ task-service puede comunicarse directamente con notification-service

---

## Fase 8: Observabilidad (Opcional - 2-4 horas)

- [ ] **8.1 - Ver logs en tiempo real**
  ```bash
  kubectl logs -f deployment/task-service -n task-platform
  ```

- [ ] **8.2 - Ver uso de recursos**
  ```bash
  kubectl top nodes
  kubectl top pods -n task-platform
  ```

- [ ] **8.3 - Instalar Prometheus (opcional)**
  ```bash
  # Requiere Helm
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
  helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
  ```

- [ ] **8.4 - Instalar Grafana (opcional)**
  ```bash
  helm repo add grafana https://grafana.github.io/helm-charts
  helm install grafana grafana/grafana -n monitoring
  ```

---

## ⏸️ Pausa / Reversión

### Si algo falla:

- [ ] **Ver qué salió mal**
  ```bash
  kubectl get events -n task-platform
  kubectl describe pod -n task-platform <pod-name>
  ```

- [ ] **Rollback rápido**
  ```bash
  kubectl rollout history deployment/task-service -n task-platform
  kubectl rollout undo deployment/task-service -n task-platform
  ```

- [ ] **Limpiar y reintentar**
  ```bash
  kubectl delete namespace task-platform
  # Editar manifests si es necesario
  kubectl apply -k kubernetes/
  ```

---

## ✅ Checklist Final

- [ ] Imágenes en Docker Hub
- [ ] Manifests YAML válidos
- [ ] Namespace creado
- [ ] Secrets y ConfigMaps aplicados
- [ ] MySQL y PostgreSQL running y healthy
- [ ] Auth, Task, Notification services running
- [ ] Services (ClusterIP) creados
- [ ] Health checks responden 200 OK
- [ ] End-to-end test pasó
- [ ] Inter-service communication funciona

---

## 📊 Resumen

| Fase | Descripción | Tiempo | Estado |
|------|-------------|--------|--------|
| **2** | Docker Hub | 1-2h | ⏳ En progreso |
| **3** | Manifests Kubernetes | 4-6h | ✅ Completado |
| **4** | Deploy en cluster | 2h | ⏳ Próximo |
| **5** | Verificación pods/services | 1-2h | ⏳ Próximo |
| **6** | End-to-End test | 1-2h | ⏳ Próximo |
| **7** | Verificar inter-servicios | 1h | ⏳ Próximo |
| **8** | Observabilidad (opt) | 2-4h | ⏳ Opcional |

**Total estimado:** 10-14 horas

---

**Creado:** Diciembre 6, 2025
**Estado:** ✅ Listo para iniciar Phase 2 (Docker Hub) y Phase 4 (Kubernetes Deploy)

