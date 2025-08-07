#!/bin/bash

# Script para verificar conectividad con PostgreSQL
# Útil para debugging de conexiones en EasyPanel

set -e

echo "🔍 Verificando conectividad con PostgreSQL..."

# Función para verificar variables de entorno
check_env_vars() {
    echo "📋 Verificando variables de entorno..."
    
    if [ -z "$DATABASE_URL" ]; then
        echo "❌ DATABASE_URL no está definida"
        exit 1
    else
        echo "✅ DATABASE_URL está definida"
        echo "   URL: ${DATABASE_URL//:*/:****@*}"  # Ocultar contraseña
    fi
}

# Función para extraer componentes de DATABASE_URL
parse_database_url() {
    echo "🔧 Parseando DATABASE_URL..."
    
    # Extraer componentes usando sed
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
    
    echo "   Usuario: $DB_USER"
    echo "   Host: $DB_HOST"
    echo "   Puerto: $DB_PORT"
    echo "   Base de datos: $DB_NAME"
}

# Función para verificar conectividad de red
check_network_connectivity() {
    echo "🌐 Verificando conectividad de red..."
    
    if ping -c 1 "$DB_HOST" > /dev/null 2>&1; then
        echo "✅ Host $DB_HOST es alcanzable"
    else
        echo "❌ No se puede alcanzar el host $DB_HOST"
        echo "   Verificar que ambos servicios estén en la misma red Docker"
        return 1
    fi
}

# Función para verificar puerto
check_port() {
    echo "🔌 Verificando puerto PostgreSQL..."
    
    if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
        echo "✅ Puerto $DB_PORT está abierto en $DB_HOST"
    else
        echo "❌ Puerto $DB_PORT no está abierto en $DB_HOST"
        return 1
    fi
}

# Función para verificar conexión PostgreSQL
check_postgres_connection() {
    echo "🐘 Verificando conexión PostgreSQL..."
    
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
        echo "✅ PostgreSQL está listo para conexiones"
    else
        echo "❌ PostgreSQL no está listo"
        return 1
    fi
}

# Función para verificar autenticación
check_authentication() {
    echo "🔐 Verificando autenticación..."
    
    # Crear archivo temporal con credenciales
    export PGPASSWORD="$DB_PASS"
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ Autenticación exitosa"
    else
        echo "❌ Error de autenticación"
        echo "   Verificar usuario y contraseña"
        return 1
    fi
    
    unset PGPASSWORD
}

# Función para verificar base de datos
check_database() {
    echo "📊 Verificando base de datos..."
    
    export PGPASSWORD="$DB_PASS"
    
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT current_database();" > /dev/null 2>&1; then
        echo "✅ Conexión a base de datos exitosa"
    else
        echo "❌ No se puede conectar a la base de datos"
        return 1
    fi
    
    unset PGPASSWORD
}

# Función principal
main() {
    echo "🚀 Iniciando verificación de conectividad..."
    echo ""
    
    # Verificar variables de entorno
    check_env_vars
    echo ""
    
    # Parsear URL
    parse_database_url
    echo ""
    
    # Verificar conectividad de red
    if ! check_network_connectivity; then
        echo "❌ Falló la verificación de red"
        exit 1
    fi
    echo ""
    
    # Verificar puerto
    if ! check_port; then
        echo "❌ Falló la verificación de puerto"
        exit 1
    fi
    echo ""
    
    # Verificar PostgreSQL
    if ! check_postgres_connection; then
        echo "❌ Falló la verificación de PostgreSQL"
        exit 1
    fi
    echo ""
    
    # Verificar autenticación
    if ! check_authentication; then
        echo "❌ Falló la verificación de autenticación"
        exit 1
    fi
    echo ""
    
    # Verificar base de datos
    if ! check_database; then
        echo "❌ Falló la verificación de base de datos"
        exit 1
    fi
    echo ""
    
    echo "🎉 ¡Todas las verificaciones pasaron exitosamente!"
    echo "✅ La aplicación puede conectarse a PostgreSQL"
}

# Ejecutar función principal
main "$@"
