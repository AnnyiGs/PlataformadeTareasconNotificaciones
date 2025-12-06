# 🔄 Instrucciones para Reiniciar la Plataforma

## ✅ Lo que está guardado:

### Backups de Bases de Datos:
- `mysql-data.tgz` (4 MB) - Datos de MySQL
- `postgres-data.tgz` (6.6 MB) - Datos de PostgreSQL
- **Ubicación:** `c:\Users\anyio\Desktop\TareasConNotificacion\PlataformadeTareasconNotificaciones\`

### Imágenes Docker:
- ✅ `andreajos/task-platform-auth-service:1.0.0`
- ✅ `andreajos/task-platform-task-service:1.0.0`
- ✅ `andreajos/task-platform-notification-service:1.0.0`
- ✅ `andreajos/task-platform-gateway:1.0.0`
- **Ubicación:** Docker Hub (público)

### Manifiestos Kubernetes:
- ✅ Todos los archivos en `kubernetes/` y `task-platform/kubernetes/deployments/`
- ✅ Configuraciones con recursos reducidos (128Mi request / 256Mi limit)

---

## 🚀 Cómo Reiniciar:

### Opción 1: Docker Compose (Desarrollo Local)
```powershell
cd c:\Users\anyio\Desktop\TareasConNotificacion\PlataformadeTareasconNotificaciones\task-platform
docker-compose up -d
```
- **Puerto Gateway:** http://localhost:8000
- **Adminer (DB GUI):** http://localhost:8080

### Opción 2: Kubernetes (Kind Cluster)
```powershell
# 1. Verificar que Docker Desktop esté corriendo
docker ps

# 2. Verificar clúster Kind
kubectl cluster-info

# 3. Reescalar deployments a valores originales
cd c:\Users\anyio\Desktop\TareasConNotificacion\PlataformadeTareasconNotificaciones

# Auth service (2 réplicas)
kubectl scale deployment auth-service -n task-platform --replicas=2

# Task service (3 réplicas)
kubectl scale deployment task-service -n task-platform --replicas=3

# Notification service (2 réplicas)
kubectl scale deployment notification-service -n task-platform --replicas=2

# 4. Verificar estado de los pods
kubectl get pods -n task-platform

# 5. (Opcional) Port-forward del Gateway
kubectl port-forward -n task-platform svc/gateway 8000:8000
```

### Si hay problemas de memoria en Kubernetes:
```powershell
# Reducir a 1 réplica por servicio
kubectl scale deployment --all --replicas=1 -n task-platform
```

---

## 🔧 Restaurar Backups (si es necesario):

### MySQL:
```powershell
# Crear pod temporal con volumen
kubectl run mysql-restore -n task-platform --image=busybox --restart=Never --overrides='{...}'

# Copiar backup
kubectl cp mysql-data.tgz task-platform/mysql-restore:/tmp/

# Extraer
kubectl exec -n task-platform mysql-restore -- sh -c "tar xzf /tmp/mysql-data.tgz -C /data"

# Limpiar
kubectl delete pod mysql-restore -n task-platform
```

### PostgreSQL:
```powershell
# Similar al proceso de MySQL, usando postgres-pvc
```

---

## 📊 Estado Actual:

- **Docker Compose:** ✅ Detenido (volúmenes preservados)
- **Kubernetes:** ⏸️ Pods escalados a 0 (PVCs intactos con 5Gi cada uno)
- **Backups:** ✅ mysql-data.tgz + postgres-data.tgz
- **Imágenes:** ✅ Publicadas en Docker Hub

---

## ⚠️ Notas Importantes:

1. **Memoria de Docker Desktop:**
   - Si Kubernetes falla por memoria insuficiente, considera:
     - Aumentar memoria en Docker Desktop Settings (6-8 GB recomendado)
     - O usar solo Docker Compose para desarrollo

2. **PVCs Kubernetes:**
   - Los PersistentVolumeClaims (`mysql-pvc` y `postgres-pvc`) **NO** se eliminan con los pods
   - Datos persisten hasta que ejecutes `kubectl delete pvc -n task-platform --all`

3. **Próximos Pasos Pendientes:**
   - Resolver problema de memoria en Kind/Docker Desktop
   - Probar E2E completo en Kubernetes
   - Configurar Ingress para acceso externo

---

## 🆘 Comandos Útiles:

```powershell
# Ver todos los contenedores
docker ps -a

# Ver estado de Kubernetes
kubectl get all -n task-platform

# Ver logs de un pod
kubectl logs -n task-platform <pod-name>

# Limpiar todo Kubernetes (¡CUIDADO! Borra datos)
kubectl delete namespace task-platform

# Reiniciar Docker Desktop
# Menú: Troubleshoot → Restart Docker Desktop
```

---

**Última actualización:** 6 de diciembre de 2025  
**Estado:** Sistema detenido de forma segura, backups completados
