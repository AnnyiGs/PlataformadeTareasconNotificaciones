# ============ Stage 1: Builder ============
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias en el builder
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============ Stage 2: Runtime ============
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Asegurar que los scripts estén en PATH
ENV PATH=/root/.local/bin:$PATH

# Copiar código fuente
COPY main.py .

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
