#!/usr/bin/env python3
"""
Script para generar y aplicar migraciones de base de datos
Uso: python scripts/migration.py [comando] [argumentos]

Comandos:
    init        - Inicializar la base de datos (crear tablas iniciales)
    generate    - Generar una nueva migración automáticamente
    migrate     - Aplicar todas las migraciones pendientes
    rollback    - Revertir la última migración
    history     - Mostrar historial de migraciones
    current     - Mostrar la migración actual
"""
import os
import sys
import subprocess
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuración
ALEMBINI_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alembic.ini')
MIGRATIONS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'alembic')


def run_command(cmd, description):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    print(f"Comando: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def init_db():
    """Crear todas las tablas usando SQLAlchemy"""
    print("\nInicializando base de datos...")
    
    try:
        from app.database import create_tables, engine
        # Importar todos los modelos para que SQLAlchemy los registre
        from app.models import (
            user, product, inventory, order, sale, recipe, cash_register,
            customer, location, notifications, settings, supplier,
            restaurant_menu, pedido_cocina, mesa, permiso
        )
        
        print("Creando tablas...")
        create_tables()
        
        # Verificar que las tablas se crearon
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n✓ Tablas creadas: {len(tables)}")
        for table in tables:
            print(f"  - {table}")
            
        print("\n✓ Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        print(f"\n✗ Error al inicializar la base de datos: {e}")
        return False


def generate_migration(message=""):
    """Generar una nueva migración"""
    if not message:
        message = input("Descripción de la migración: ") or f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    cmd = [
        "python", "-m", "alembic",
        "revision",
        "--autogenerate",
        "-m", message,
        "-c", ALEMBINI_PATH
    ]
    
    return run_command(cmd, f"Generando migración: {message}")


def migrate():
    """Aplicar migraciones"""
    cmd = [
        "python", "-m", "alembic",
        "upgrade", "head",
        "-c", ALEMBINI_PATH
    ]
    
    return run_command(cmd, "Aplicando migraciones")


def rollback():
    """Revertir última migración"""
    cmd = [
        "python", "-m", "alembic",
        "upgrade", "-1",
        "-c", ALEMBINI_PATH
    ]
    
    return run_command(cmd, "Revirtiendo migración")


def history():
    """Mostrar historial de migraciones"""
    cmd = [
        "python", "-m", "alembic",
        "history",
        "-c", ALEMBINI_PATH
    ]
    
    return run_command(cmd, "Historial de migraciones")


def current():
    """Mostrar migración actual"""
    cmd = [
        "python", "-m", "alembic",
        "current",
        "-c", ALEMBINI_PATH
    ]
    
    return run_command(cmd, "Migración actual")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nComandos disponibles:")
        print("  init        - Crear tablas iniciales (sin migraciones)")
        print("  generate    - Generar nueva migración")
        print("  migrate     - Aplicar migraciones")
        print("  rollback    - Revertir última migración")
        print("  history     - Ver historial")
        print("  current     - Ver migración actual")
        return 1
    
    command = sys.argv[1].lower()
    
    commands = {
        "init": init_db,
        "generate": lambda: generate_migration(" ".join(sys.argv[2:])),
        "migrate": migrate,
        "rollback": rollback,
        "history": history,
        "current": current,
    }
    
    if command not in commands:
        print(f"✗ Comando desconocido: {command}")
        return 1
    
    return commands[command]()


if __name__ == "__main__":
    sys.exit(main())
