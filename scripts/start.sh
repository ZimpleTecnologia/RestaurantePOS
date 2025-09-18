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
    
    # Verificar base de datos primero
    if [ -f "verify_database.py" ]; then
        echo "🔍 Verificando estructura de base de datos..."
        if python verify_database.py; then
            echo "✅ Base de datos ya está actualizada"
            return 0
        else
            echo "⚠️  Base de datos necesita migración"
        fi
    fi
    
    # Ejecutar migración personalizada
    if [ -f "migrate_database.py" ]; then
        echo "🔧 Ejecutando migración personalizada..."
        if python migrate_database.py; then
            echo "✅ Migración personalizada completada"
        else
            echo "⚠️  Error en migración personalizada"
        fi
    fi
    
    # Verificar si alembic está disponible
    if command -v alembic &> /dev/null; then
        echo "🔧 Ejecutando migraciones de Alembic..."
        alembic upgrade head || echo "⚠️  No se pudieron ejecutar las migraciones de Alembic"
    else
        echo "ℹ️  Alembic no está disponible, saltando migraciones de Alembic"
    fi
    
    # Verificar nuevamente después de las migraciones
    if [ -f "verify_database.py" ]; then
        echo "🔍 Verificando base de datos después de migraciones..."
        python verify_database.py || echo "⚠️  Base de datos aún necesita atención"
    fi
}

# Función para verificar directorios necesarios
verify_directories() {
    echo "📁 Verificando directorios necesarios..."
    
    # Verificar que los directorios existen
    if [ ! -d "uploads/products" ]; then
        echo "⚠️  Directorio uploads/products no existe"
    else
        echo "✅ Directorio uploads/products existe"
    fi
    
    if [ ! -d "uploads/reports" ]; then
        echo "⚠️  Directorio uploads/reports no existe"
    else
        echo "✅ Directorio uploads/reports existe"
    fi
    
    if [ ! -d "logs" ]; then
        echo "⚠️  Directorio logs no existe"
    else
        echo "✅ Directorio logs existe"
    fi
}

# Función principal
main() {
    # Verificar directorios
    verify_directories
    
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
