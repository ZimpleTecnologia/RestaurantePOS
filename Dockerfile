# Dockerfile para Sistema POS
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar archivo de dependencias primero (para aprovechar la caché de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Crear directorios necesarios
RUN mkdir -p uploads static templates

# Copiar código de la aplicación (después de instalar dependencias para mejor caché)
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 