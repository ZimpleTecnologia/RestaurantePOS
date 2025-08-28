#!/bin/bash

# Script para limpiar la base de datos del Sistema POS
# Ejecuta el script de limpieza de Python

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar si Docker está ejecutándose
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker no está ejecutándose. Inicia Docker primero."
        exit 1
    fi
}

# Función para verificar si los contenedores están ejecutándose
check_containers() {
    print_message "Verificando contenedores del Sistema POS..."
    
    if ! docker ps | grep -q "sistema_pos_app"; then
        print_warning "El contenedor de la aplicación no está ejecutándose."
        print_message "¿Quieres iniciar los contenedores primero? (sí/no)"
        read -r response
        if [[ $response =~ ^[SsYy] ]]; then
            print_message "Iniciando contenedores..."
            cd "$(dirname "$0")/.."
            docker-compose up -d
            print_message "Esperando 10 segundos para que los servicios estén listos..."
            sleep 10
        else
            print_error "Los contenedores deben estar ejecutándose para limpiar la base de datos."
            exit 1
        fi
    fi
    
    if ! docker ps | grep -q "sistema_pos_db"; then
        print_error "El contenedor de la base de datos no está ejecutándose."
        exit 1
    fi
    
    print_success "Contenedores verificados"
}

# Función para ejecutar el script de limpieza
run_cleanup() {
    print_message "Ejecutando script de limpieza..."
    
    # Obtener el directorio del script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Cambiar al directorio del proyecto
    cd "$PROJECT_DIR"
    
    # Verificar que el script existe
    if [ ! -f "scripts/clean_database.py" ]; then
        print_error "No se encontró el script clean_database.py"
        exit 1
    fi
    
    # Ejecutar el script de limpieza
    print_message "Ejecutando: python scripts/clean_database.py"
    python scripts/clean_database.py
    
    if [ $? -eq 0 ]; then
        print_success "Limpieza completada exitosamente"
    else
        print_error "Error durante la limpieza"
        exit 1
    fi
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help     Mostrar esta ayuda"
    echo "  -f, --force    Ejecutar sin confirmación"
    echo "  -y, --yes      Confirmar automáticamente"
    echo ""
    echo "Descripción:"
    echo "  Este script limpia todos los datos de la base de datos del Sistema POS"
    echo "  manteniendo solo el usuario administrador."
    echo ""
    echo "Ejemplos:"
    echo "  $0              # Ejecutar con confirmación interactiva"
    echo "  $0 --force      # Ejecutar sin verificar contenedores"
    echo "  $0 --yes        # Confirmar automáticamente"
}

# Variables de control
FORCE_MODE=false
AUTO_CONFIRM=false

# Procesar argumentos de línea de comandos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE_MODE=true
            shift
            ;;
        -y|--yes)
            AUTO_CONFIRM=true
            shift
            ;;
        *)
            print_error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Función principal
main() {
    echo "=" * 60
    echo "🧹 SCRIPT DE LIMPIEZA DE BASE DE DATOS - SISTEMA POS"
    echo "=" * 60
    echo ""
    
    # Verificar Docker (a menos que esté en modo force)
    if [ "$FORCE_MODE" = false ]; then
        check_docker
        check_containers
    fi
    
    # Confirmación final (a menos que esté en modo auto-confirm)
    if [ "$AUTO_CONFIRM" = false ]; then
        print_warning "¿Estás seguro de que quieres limpiar TODA la base de datos?"
        print_warning "Esta acción NO se puede deshacer!"
        echo ""
        read -r -p "Escribe 'LIMPIAR' para continuar: " confirmation
        
        if [ "$confirmation" != "LIMPIAR" ]; then
            print_message "Operación cancelada"
            exit 0
        fi
    fi
    
    # Ejecutar limpieza
    run_cleanup
    
    print_success "Proceso completado!"
    echo ""
    print_message "Próximos pasos:"
    echo "  1. Reinicia la aplicación si es necesario"
    echo "  2. Accede con las credenciales del admin"
    echo "  3. Comienza a configurar tu sistema desde cero"
    echo ""
    print_message "Credenciales del admin:"
    echo "  Usuario: admin"
    echo "  Contraseña: admin123"
}

# Ejecutar función principal
main "$@"
