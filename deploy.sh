#!/bin/bash

# Script de despliegue para EasyPanel
# Uso: ./deploy.sh v1.2.0

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Uso: ./deploy.sh <version>"
    echo "Ejemplo: ./deploy.sh v1.2.0"
    exit 1
fi

echo "🚀 Iniciando despliegue de la versión $VERSION..."

# 1. Construir la imagen
echo "📦 Construyendo imagen Docker..."
docker build -t zimpletecnologia/app_pos:$VERSION .

if [ $? -ne 0 ]; then
    echo "❌ Error al construir la imagen"
    exit 1
fi

# 2. Subir a Docker Hub
echo "⬆️ Subiendo imagen a Docker Hub..."
docker push zimpletecnologia/app_pos:$VERSION

if [ $? -ne 0 ]; then
    echo "❌ Error al subir la imagen"
    exit 1
fi

# 3. Actualizar docker-compose.easypanel.yml
echo "📝 Actualizando configuración..."
sed -i "s/zimpletecnologia\/app_pos:v[0-9.]*/zimpletecnologia\/app_pos:$VERSION/" docker-compose.easypanel.yml

# 4. Instrucciones para el VPS
echo "✅ Imagen construida y subida exitosamente!"
echo ""
echo "📋 Próximos pasos en tu VPS:"
echo "1. cd /path/to/your/project"
echo "2. docker pull zimpletecnologia/app_pos:$VERSION"
echo "3. docker-compose -f docker-compose.easypanel.yml down"
echo "4. docker-compose -f docker-compose.easypanel.yml up -d"
echo "5. docker-compose -f docker-compose.easypanel.yml logs -f app"
echo ""
echo "🌐 O usar EasyPanel UI para cambiar la imagen a: zimpletecnologia/app_pos:$VERSION"
