#!/usr/bin/env python3
"""
Script para inicializar las mesas por defecto del restaurante
"""
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.table_service import TableService
# No necesitamos AuthService para este script

def inicializar_mesas():
    """Inicializar mesas por defecto"""
    db = SessionLocal()
    
    try:
        print("🏪 Inicializando mesas del restaurante...")
        
        # Crear mesas por defecto
        mesas_creadas = TableService.initialize_default_tables(db)
        
        print(f"✅ Se crearon {len(mesas_creadas)} mesas exitosamente:")
        print()
        
        for mesa in mesas_creadas:
            print(f"  📍 {mesa.name} ({mesa.table_number})")
            print(f"     Capacidad: {mesa.capacity} personas")
            print(f"     Ubicación: {mesa.location}")
            print(f"     Estado: {mesa.status}")
            print()
        
        print("🎉 Inicialización completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    inicializar_mesas()
