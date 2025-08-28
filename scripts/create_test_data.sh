#!/bin/bash

# Script para crear datos de prueba del Sistema POS
# Ejecuta el script de creación de datos de prueba

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
            print_error "Los contenedores deben estar ejecutándose para crear datos de prueba."
            exit 1
        fi
    fi
    
    if ! docker ps | grep -q "sistema_pos_db"; then
        print_error "El contenedor de la base de datos no está ejecutándose."
        exit 1
    fi
    
    print_success "Contenedores verificados"
}

# Función para ejecutar el script de creación de datos
run_create_test_data() {
    print_message "Ejecutando script de creación de datos de prueba..."
    
    # Obtener el directorio del script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Cambiar al directorio del proyecto
    cd "$PROJECT_DIR"
    
    # Verificar que el script existe
    if [ ! -f "scripts/create_complete_test_data.py" ]; then
        print_error "No se encontró el script create_complete_test_data.py"
        exit 1
    fi
    
    # Ejecutar el script de creación de datos
    print_message "Ejecutando: python scripts/create_complete_test_data.py"
    python scripts/create_complete_test_data.py
    
    if [ $? -eq 0 ]; then
        print_success "Datos de prueba creados exitosamente"
    else
        print_error "Error durante la creación de datos de prueba"
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
    echo "  Este script crea datos de prueba completos para el Sistema POS"
    echo "  incluyendo usuarios, productos, clientes, proveedores, etc."
    echo ""
    echo "Datos que se crearán:"
    echo "  👥 Usuarios (admin, meseros, cocineros, caja, almacén)"
    echo "  🍽️ Productos (categorías, subcategorías, productos)"
    echo "  👤 Clientes (personas naturales y jurídicas)"
    echo "  🏢 Proveedores (distribuidores, carnicerías, bebidas)"
    echo "  🪑 Mesas (8 mesas con diferentes capacidades)"
    echo "  ⚙️ Configuraciones del sistema"
    echo "  💰 Ventas de ejemplo"
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
    echo "=" * 70
    echo "🎯 CREACIÓN DE DATOS DE PRUEBA - SISTEMA POS"
    echo "=" * 70
    echo ""
    
    # Verificar Docker (a menos que esté en modo force)
    if [ "$FORCE_MODE" = false ]; then
        check_docker
        check_containers
    fi
    
    # Confirmación final (a menos que esté en modo auto-confirm)
    if [ "$AUTO_CONFIRM" = false ]; then
        print_warning "¿Estás seguro de que quieres crear datos de prueba?"
        print_warning "Esto agregará datos al sistema existente."
        echo ""
        read -r -p "Escribe 'CREAR' para continuar: " confirmation
        
        if [ "$confirmation" != "CREAR" ]; then
            print_message "Operación cancelada"
            exit 0
        fi
    fi
    
    # Ejecutar creación de datos
    run_create_test_data
    
    print_success "Proceso completado!"
    echo ""
    print_message "Próximos pasos:"
    echo "  1. Accede al sistema con las credenciales mostradas"
    echo "  2. Explora todas las funcionalidades"
    echo "  3. Prueba crear ventas, órdenes, etc."
    echo "  4. Verifica que todos los módulos funcionen"
    echo ""
    print_message "Credenciales disponibles:"
    echo "  Admin: admin / admin123"
    echo "  Mesero: mesero1 / mesero123"
    echo "  Cocina: cocinero1 / cocina123"
    echo "  Caja: caja1 / caja123"
    echo "  Almacén: almacen1 / almacen123"
}

# Ejecutar función principal
main "$@"
