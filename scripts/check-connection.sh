#!/bin/bash

# Script para verificar conectividad con PostgreSQL
# Útil para debugging de conexiones en EasyPanel

set -e

# Cargar variables de entorno desde .env
if [ -f ".env" ]; then
    echo "📄 Cargando variables de entorno desde .env..."
    export $(grep -v '^#' .env | xargs)
    echo "✅ Variables de entorno cargadas"
else
    echo "❌ Archivo .env no encontrado"
    exit 1
fi

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
    
    # Si estamos en localhost, saltar la verificación de ping
    if [ "$DB_HOST" = "localhost" ] || [ "$DB_HOST" = "127.0.0.1" ]; then
        echo "✅ Host $DB_HOST (localhost) - saltando verificación de ping"
        return 0
    fi
    
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
    
    # Intentar diferentes métodos para verificar el puerto
    if command -v nc >/dev/null 2>&1; then
        # Usar netcat si está disponible
        if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
            echo "✅ Puerto $DB_PORT está abierto en $DB_HOST"
            return 0
        fi
    elif command -v telnet >/dev/null 2>&1; then
        # Usar telnet como alternativa
        if timeout 5 bash -c "</dev/tcp/$DB_HOST/$DB_PORT" 2>/dev/null; then
            echo "✅ Puerto $DB_PORT está abierto en $DB_HOST"
            return 0
        fi
    else
        # En Windows, intentar con PowerShell
        if powershell -Command "Test-NetConnection -ComputerName $DB_HOST -Port $DB_PORT -InformationLevel Quiet" 2>/dev/null; then
            echo "✅ Puerto $DB_PORT está abierto en $DB_HOST"
            return 0
        fi
    fi
    
    echo "❌ Puerto $DB_PORT no está abierto en $DB_HOST"
    echo "   Verificar que PostgreSQL esté ejecutándose en el puerto $DB_PORT"
    return 1
}

# Función para verificar Docker (simplificada para Windows)
check_docker_status() {
    echo "🐳 Verificando estado de Docker..."
    
    if docker ps | grep -q "sistema_pos_db"; then
        echo "✅ Contenedor sistema_pos_db está ejecutándose"
        return 0
    else
        echo "❌ Contenedor sistema_pos_db no está ejecutándose"
        return 1
    fi
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
    
    # Verificar Docker
    if ! check_docker_status; then
        echo "❌ Falló la verificación de Docker"
        exit 1
    fi
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
    
    echo "🎉 ¡Verificaciones básicas completadas exitosamente!"
    echo "✅ La aplicación debería poder conectarse a PostgreSQL"
    echo ""
    echo "📝 Para verificar la conexión completa, ejecuta la aplicación:"
    echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
}

# Ejecutar función principal
main "$@"
