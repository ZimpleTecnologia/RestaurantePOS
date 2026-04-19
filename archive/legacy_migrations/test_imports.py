#!/usr/bin/env python3
"""
Script para verificar que no hay errores de importación en los modelos
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Probar las importaciones de los modelos"""
    print("🔍 Verificando importaciones...")
    
    try:
        print("📦 Importando modelos de restaurant_menu...")
        from app.models.restaurant_menu import (
            CategoriaMenuRestaurante, 
            PlatoRestaurante, 
            MenuDia, 
            MenuCategoriaPlato, 
            AcompanamientoFijo
        )
        print("✅ Modelos importados correctamente")
        
        print("📦 Importando schemas...")
        from app.schemas.restaurant_menu import (
            CategoriaMenuCreate,
            PlatoRestauranteCreate,
            MenuDiaCreate
        )
        print("✅ Schemas importados correctamente")
        
        print("📦 Importando router...")
        from app.routers.restaurant_menu import router
        print("✅ Router importado correctamente")
        
        print("📦 Verificando configuración de base de datos...")
        from app.database import get_db
        print("✅ Base de datos configurada correctamente")
        
        print("\n🎉 Todas las importaciones funcionan correctamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ El sistema está listo para funcionar")
    else:
        print("\n❌ Hay problemas que necesitan ser corregidos")

