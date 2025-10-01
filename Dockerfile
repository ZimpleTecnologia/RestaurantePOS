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

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copiar scripts de utilidad desde el directorio scripts
COPY scripts/create_admin_user.py ./create_admin.py
COPY scripts/create_complete_test_data.py ./create_test_data.py
COPY init_db.py ./
COPY scripts/reset_admin_password.py ./reset_admin_password.py
COPY migrate_database.py ./
COPY scripts/check_database_tables.py ./verify_database.py

# Script de inicio que espera a que la BD esté disponible
COPY scripts/start.sh /app/start.sh

# Crear directorios necesarios con permisos correctos
RUN mkdir -p uploads/products uploads/reports static templates logs && \
    chown -R appuser:appuser /app && \
    chmod -R 755 uploads logs && \
    chmod +x /app/start.sh

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

# Comando para ejecutar la aplicación

CMD ["/app/start.sh"] 

