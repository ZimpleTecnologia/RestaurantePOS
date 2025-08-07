#!/bin/bash

# Script de inicio para Sistema POS
# Espera a que la base de datos esté disponible antes de iniciar la aplicación

set -e

echo "🚀 Iniciando Sistema POS..."

# Función para esperar a que PostgreSQL esté disponible
wait_for_postgres() {
    echo "⏳ Esperando a que PostgreSQL esté disponible..."
    
    # Extraer host y puerto de DATABASE_URL
    if [ -n "$DATABASE_URL" ]; then
        # Parsear DATABASE_URL para obtener host y puerto
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [ -z "$DB_HOST" ]; then
            DB_HOST="zimple_postgresql"
        fi
        if [ -z "$DB_PORT" ]; then
            DB_PORT="5432"
        fi
    else
        DB_HOST="zimple_postgresql"
        DB_PORT="5432"
    fi
    
    echo "📍 Conectando a PostgreSQL en $DB_HOST:$DB_PORT"
    
    # Esperar hasta que PostgreSQL esté disponible
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U sistema_pos_user; do
        echo "⏳ PostgreSQL no está listo aún... esperando 5 segundos"
        sleep 5
    done
    
    echo "✅ PostgreSQL está disponible!"
}

# Función para ejecutar migraciones
run_migrations() {
    echo "🔄 Ejecutando migraciones de base de datos..."
    
    # Verificar si alembic está disponible
    if command -v alembic &> /dev/null; then
        alembic upgrade head || echo "⚠️  No se pudieron ejecutar las migraciones automáticamente"
    else
        echo "ℹ️  Alembic no está disponible, saltando migraciones"
    fi
}

# Función para crear directorios necesarios
create_directories() {
    echo "📁 Creando directorios necesarios..."
    
    # Crear directorios si no existen
    mkdir -p uploads logs
    
    # Intentar cambiar permisos solo si es posible
    if [ -w uploads ]; then
        chmod 755 uploads 2>/dev/null || echo "ℹ️  No se pudieron cambiar permisos de uploads"
    fi
    
    if [ -w logs ]; then
        chmod 755 logs 2>/dev/null || echo "ℹ️  No se pudieron cambiar permisos de logs"
    fi
    
    echo "✅ Directorios creados/verificados"
}

# Función principal
main() {
    # Crear directorios
    create_directories
    
    # Esperar a PostgreSQL
    wait_for_postgres
    
    # Ejecutar migraciones
    run_migrations
    
    echo "🎯 Iniciando aplicación..."
    
    # Iniciar la aplicación
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 1 \
        --log-level info
}

# Ejecutar función principal
main "$@"
