# Dockerfile para Laura Memory Service - Production Ready
FROM python:3.11-slim

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs tests/cassettes /tmp \
    && chown -R app:app /app \
    && chmod -R 755 /app/logs

# Cambiar a usuario no-root
USER app

# Exponer puerto
EXPOSE 5001

# Variables de entorno por defecto
ENV FLASK_ENV=production
ENV FLASK_APP=server.py
ENV PYTHONPATH=/app
ENV GUNICORN_WORKERS=4
ENV LOG_LEVEL=INFO

# Health check mejorado
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Comando para ejecutar con Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "server:app"]