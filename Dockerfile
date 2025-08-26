# Dockerfile para Sistema POS
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para bcrypt
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar archivo de dependencias primero
COPY requirements.txt .

# Instalar dependencias de Python con orden específico para bcrypt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir bcrypt==4.0.1 && \
    pip install --no-cache-dir passlib==1.7.4 && \
    pip install --no-cache-dir -r requirements.txt

# Crear directorios necesarios
RUN mkdir -p uploads static templates

# Copiar código de la aplicación
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

# Copiar scripts de utilidad
COPY create_admin.py ./
COPY create_test_data.py ./
COPY init_db.py ./
COPY start.sh ./

# Hacer el script ejecutable
RUN chmod +x start.sh

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# Comando para ejecutar la aplicación
CMD ["./start.sh"] 