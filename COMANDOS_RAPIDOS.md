# 📋 COMANDOS RÁPIDOS PARA COPIAR Y PEGAR

## 1️⃣ PREPARACIÓN INICIAL (Copy & Paste Todo)

```powershell
cd c:\Users\anyio\Desktop\TareasConNotificacion\PlataformadeTareasconNotificaciones\task-platform

docker-compose down --remove-orphans

docker-compose up -d

Start-Sleep -Seconds 45

docker-compose ps
```

---

## 2️⃣ REGISTRAR USUARIO NORMAL

```powershell
$userResp = Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=demo1@example.com&password=demo123&role=user" -Method POST
$userResp | Format-List
$userToken = $userResp.access_token
$userId = $userResp.id
Write-Host "✅ Usuario ID=$userId registrado"
```

---

## 3️⃣ REGISTRAR ADMIN

```powershell
$adminResp = Invoke-RestMethod -Uri "http://localhost:8001/auth/register?email=admin27@example.com&password=admin123&role=admin" -Method POST
$adminResp | Format-List
$adminToken = $adminResp.access_token
$adminId = $adminResp.id
Write-Host "✅ Admin ID=$adminId registrado"
```

---

## 4️⃣ CREAR TAREA (COMO ADMIN)

```powershell
$adminHeaders = @{
    "Authorization" = "Bearer $adminToken"
    "Content-Type" = "application/json"
}

$taskBody = @{
    title = "Demostración en clase"
    description = "Presentar arquitectura de microservicios en Docker"
    assigned_to = $userId
} | ConvertTo-Json

$taskResp = Invoke-RestMethod -Uri "http://localhost:8002/tasks/" -Method POST -Headers $adminHeaders -Body $taskBody
$taskResp | Format-List
$taskId = $taskResp.task_id
Write-Host "✅ Tarea ID=$taskId creada"
```

---

## 5️⃣ VER TAREAS DEL USUARIO

```powershell
$userHeaders = @{
    "Authorization" = "Bearer $userToken"
    "Content-Type" = "application/json"
}

$tasksResp = Invoke-RestMethod -Uri "http://localhost:8002/tasks/assigned" -Method GET -Headers $userHeaders
$tasksResp | Format-Table -AutoSize
```

---

## 6️⃣ VER NOTIFICACIONES

```powershell
$notifResp = Invoke-RestMethod -Uri "http://localhost:8003/notifications/" -Method GET -Headers $userHeaders
$notifResp | Format-Table -AutoSize
```

---

## 7️⃣ INTENTO DE ATAQUE (Usuario intenta crear tarea)

```powershell
$taskBody2 = @{
    title = "Intento de ataque"
    description = "Usuario normal intenta crear tarea"
    assigned_to = $adminId
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8002/tasks/" -Method POST -Headers $userHeaders -Body $taskBody2
    Write-Host "❌ ERROR: Debería haber sido rechazado"
} catch {
    Write-Host "✅ CORRECTO: Acceso denegado (403)" -ForegroundColor Green
}
```

---

## 8️⃣ ABRIR ADMINER (Base de Datos Web UI)

```powershell
Start-Process "http://localhost:8080"
```

---

## 🔚 APAGAR TODO

```powershell
docker-compose down
```

---

**Duración total: 10-15 minutos** ⏱️
