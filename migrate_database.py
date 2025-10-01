#!/usr/bin/env python3
"""
Script de migración de base de datos
Se ejecuta para aplicar migraciones de Alembic
"""
import sys
import os
import subprocess

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

def run_migrations():
    """Ejecutar migraciones de Alembic"""
    try:
        print("🔄 Ejecutando migraciones de base de datos...")
        
        # Ejecutar alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd="/app"
        )
        
        if result.returncode == 0:
            print("✅ Migraciones ejecutadas exitosamente")
            print(result.stdout)
            return True
        else:
            print("❌ Error ejecutando migraciones:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando migraciones de base de datos...")
    
    success = run_migrations()
    
    if success:
        print("✅ Migraciones completadas exitosamente")
    else:
        print("❌ Error en las migraciones")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


