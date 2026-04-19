"""
Script de migración para crear las tablas del módulo de Pedidos a Cocina
Ejecutar este script para crear las tablas necesarias en la base de datos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings
from app.database import Base
from app.models.pedido_cocina import PedidoCocina, PedidoDetalle, PedidoMenuOpcion

def create_tables():
    """Crear las tablas del módulo de pedidos a cocina"""
    engine = create_engine(settings.database_url)
    
    print("🔧 Creando tablas del módulo de Pedidos a Cocina...")
    
    try:
        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(bind=engine, tables=[
            PedidoCocina.__table__,
            PedidoDetalle.__table__,
            PedidoMenuOpcion.__table__
        ])
        
        print("✅ Tablas creadas exitosamente:")
        print("   - pedidos_cocina")
        print("   - pedidos_detalle")
        print("   - pedidos_menu_opciones")
        
        return True
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Módulo de Pedidos a Cocina")
    print("=" * 60)
    print()
    
    if create_tables():
        print()
        print("✅ Migración completada exitosamente")
    else:
        print()
        print("❌ La migración falló. Revisa los errores anteriores.")
        sys.exit(1)

