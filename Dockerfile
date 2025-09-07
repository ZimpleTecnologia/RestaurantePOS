# Dockerfile para Sistema POS - Producción con BD independiente
FROM python:3.9-slim

# Establecer variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para bcrypt
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar archivo de dependencias primero
COPY requirements.txt .

# Instalar dependencias de Python con orden específico para bcrypt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir bcrypt==4.0.1 && \
    pip install --no-cache-dir passlib==1.7.4 && \
    pip install --no-cache-dir -r requirements.txt

# Crear directorios necesarios con permisos correctos
RUN mkdir -p uploads static templates logs && \
    chown -R appuser:appuser /app && \
    chmod 755 uploads logs

# Copiar código de la aplicación
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/


# Copiar scripts de utilidad
COPY create_admin.py ./
COPY create_test_data.py ./
COPY init_db.py ./

# Cambiar propietario de todos los archivos
RUN chown -R appuser:appuser /app

# Cambiar al usuario no-root
USER appuser


# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=false

# Health check mejorado para servicios independientes
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Script de inicio que espera a que la BD esté disponible
COPY --chown=appuser:appuser scripts/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Comando para ejecutar la aplicación

CMD ["/app/start.sh"] 

