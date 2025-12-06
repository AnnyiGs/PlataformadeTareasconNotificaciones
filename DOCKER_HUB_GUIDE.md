# Publicar Imágenes en Docker Hub - Guía Técnica

## Pre-requisitos

1. Crear cuenta en [Docker Hub](https://hub.docker.com)
2. Instalar Docker Desktop
3. Estar logueado: `docker login`

---

## Paso 1: Crear Repositorios en Docker Hub

### Via Dashboard Web

1. Ir a https://hub.docker.com/
2. Click en "Create Repository"
3. Crear 3 repositorios:
   - `task-platform-auth-service`
   - `task-platform-task-service`
   - `task-platform-notification-service`
4. Configurar como **Public** (para pulls sin autenticación)

---

## Paso 2: Etiquetar Imágenes Locales

```powershell
# Ver imágenes locales
docker images | grep task-platform

# Etiquetar para Docker Hub
# Formato: docker tag <local-image> <docker-hub-user>/<repository>:<tag>

docker tag task-platform-auth-service:latest annyigs/task-platform-auth-service:latest
docker tag task-platform-task-service:latest annyigs/task-platform-task-service:latest
docker tag task-platform-notification-service:latest annyigs/task-platform-notification-service:latest

# Opcionalmente agregar versión
docker tag task-platform-auth-service:latest annyigs/task-platform-auth-service:1.0.0
docker tag task-platform-task-service:latest annyigs/task-platform-task-service:1.0.0
docker tag task-platform-notification-service:latest annyigs/task-platform-notification-service:1.0.0
```

### Verificar etiquetado
```powershell
docker images | grep annyigs
# OUTPUT:
# annyigs/task-platform-auth-service              latest      <hash>    220MB
# annyigs/task-platform-task-service              latest      <hash>    210MB
# annyigs/task-platform-notification-service      latest      <hash>    210MB
```

---

## Paso 3: Pushear a Docker Hub

```powershell
# Hacer push de latest tags
docker push annyigs/task-platform-auth-service:latest
docker push annyigs/task-platform-task-service:latest
docker push annyigs/task-platform-notification-service:latest

# Hacer push de version tags
docker push annyigs/task-platform-auth-service:1.0.0
docker push annyigs/task-platform-task-service:1.0.0
docker push annyigs/task-platform-notification-service:1.0.0
```

### Ejemplo de salida:
```
Using default tag: latest
The push refers to repository [docker.io/annyigs/task-platform-auth-service]
5f70bf18a086: Pushed
ab8c5fe4f630: Pushed
a3ed95caeb02: Pushed
latest: digest: sha256:abc123... size: 1234
```

---

## Paso 4: Verificar en Docker Hub

1. Ir a https://hub.docker.com/r/annyigs/task-platform-auth-service
2. Ver:
   - Tags: `latest`, `1.0.0`
   - Image size: ~220MB
   - Pull command: `docker pull annyigs/task-platform-auth-service:latest`

---

## Paso 5: Usar en Docker Compose

Ahora puedes referenciar Docker Hub en lugar de `build`:

```yaml
# docker-compose.yml
services:
  auth-service:
    # Opción 1: Build local (actual)
    build: ./auth-service
    
    # Opción 2: Descargar de Docker Hub
    image: annyigs/task-platform-auth-service:latest
    
  task-service:
    image: annyigs/task-platform-task-service:latest
    
  notification-service:
    image: annyigs/task-platform-notification-service:latest
```

### Usar Docker Hub version en Docker Compose:
```powershell
# Detener stack local
docker compose down

# Actualizar docker-compose.yml para usar imágenes de Docker Hub
# (reemplazar "build: ./..." con "image: annyigs/...")

# Correr stack remoto
docker compose up -d
# Docker descargará imágenes de Docker Hub automáticamente
```

---

## Paso 6: Usar en Kubernetes

```yaml
# kubernetes/deployments/auth-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: annyigs/task-platform-auth-service:latest
        imagePullPolicy: IfNotPresent  # o Always para latest
        ports:
        - containerPort: 8001
        env:
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jwt-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Paso 7: Automatizar con CI/CD (GitHub Actions)

Crear `.github/workflows/docker-push.yml`:

```yaml
name: Build and Push to Docker Hub

on:
  push:
    branches: [main]
    paths:
      - 'task-platform/auth-service/**'
      - 'task-platform/task-service/**'
      - 'task-platform/notification-service/**'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    # Build Auth Service
    - name: Build and Push Auth Service
      uses: docker/build-push-action@v4
      with:
        context: ./task-platform/auth-service
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/task-platform-auth-service:latest
          ${{ secrets.DOCKER_USERNAME }}/task-platform-auth-service:${{ github.sha }}
    
    # Build Task Service
    - name: Build and Push Task Service
      uses: docker/build-push-action@v4
      with:
        context: ./task-platform/task-service
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/task-platform-task-service:latest
          ${{ secrets.DOCKER_USERNAME }}/task-platform-task-service:${{ github.sha }}
    
    # Build Notification Service
    - name: Build and Push Notification Service
      uses: docker/build-push-action@v4
      with:
        context: ./task-platform/notification-service
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/task-platform-notification-service:latest
          ${{ secrets.DOCKER_USERNAME }}/task-platform-notification-service:${{ github.sha }}
```

### Configurar secretos en GitHub:
1. Repo → Settings → Secrets and Variables → Actions
2. Agregar:
   - `DOCKER_USERNAME`: tu username de Docker Hub
   - `DOCKER_PASSWORD`: tu token de acceso (no contraseña)

---

## Troubleshooting

### Error: "denied: requested access to the resource is denied"
```
Solución: docker login
Verificar credenciales en ~/.docker/config.json
```

### Error: "unknown flag: --user"
```
Asegurarse que se está usando la versión correcta de pip:
pip install --user --no-cache-dir packages
```

### Imágenes muy grandes
```
Verificar tamaño:
docker image ls
docker image history annyigs/task-platform-auth-service:latest

Optimizar:
- Usar .dockerignore
- Limpiar __pycache__
- Usar multi-stage builds ✅ (ya implementado)
```

### Pull lento desde Kubernetes
```
Agregar imagePullPolicy: IfNotPresent en deployment
O configurar private registry si está en firewall
```

---

## Checklist

- [ ] Crear cuenta en Docker Hub
- [ ] Crear 3 repositorios públicos
- [ ] Instalar Docker Desktop
- [ ] Hacer `docker login`
- [ ] Etiquetar imágenes locales con `docker tag`
- [ ] Hacer push: `docker push annyigs/...`
- [ ] Verificar en https://hub.docker.com
- [ ] (Opcional) Configurar CI/CD en GitHub Actions
- [ ] (Opcional) Usar imágenes en docker-compose.yml remoto
- [ ] (Kubernetes) Usar imágenes en manifests K8s

---

## Comandos Rápidos

```powershell
# Ver imágenes locales
docker images

# Etiquetar todas
docker tag task-platform-auth-service:latest annyigs/task-platform-auth-service:latest
docker tag task-platform-task-service:latest annyigs/task-platform-task-service:latest
docker tag task-platform-notification-service:latest annyigs/task-platform-notification-service:latest

# Hacer push
docker push annyigs/task-platform-auth-service:latest
docker push annyigs/task-platform-task-service:latest
docker push annyigs/task-platform-notification-service:latest

# Limpiar localmente (opcional)
docker rmi task-platform-auth-service:latest
docker rmi task-platform-task-service:latest
docker rmi task-platform-notification-service:latest
```

---

## Después de Pushear: Kubernetes Deploy

```bash
# 1. Crear secrets para JWT
kubectl create secret generic jwt-secrets \
  --from-literal=secret-key=your-secret-jwt-key-change-in-production-12345

# 2. Aplicar deployments
kubectl apply -f kubernetes/manifests/

# 3. Verificar pods
kubectl get pods
kubectl logs deployment/task-service

# 4. Port forward para testing
kubectl port-forward svc/task-service 8002:8002

# 5. Testear
curl http://localhost:8002/health
```

---

**Estado:** Las imágenes están listas para subirse a Docker Hub.
Próximo: Crear manifests Kubernetes y hacer deploy.

