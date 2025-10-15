#!/usr/bin/env python3
"""
Script para probar las relaciones del modelo MenuDiaRestructured
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.menu_restructured import MenuDiaRestructured, OpcionPlato, MenuDiaOpcion
from sqlalchemy.orm import Session

def test_model_relations():
    """Probar que las relaciones del modelo funcionen correctamente"""
    try:
        print("🔍 Probando relaciones del modelo MenuDiaRestructured...")
        
        # Obtener sesión de base de datos
        db = next(get_db())
        
        # Probar consulta básica
        print("📊 Consultando menús...")
        menus = db.query(MenuDiaRestructured).limit(5).all()
        print(f"   ✅ Encontrados {len(menus)} menús")
        
        for menu in menus:
            print(f"   📋 Menú: {menu.nombre} (ID: {menu.id})")
            print(f"      Fecha: {menu.fecha}")
            print(f"      Estado: {menu.estado}")
            
            # Probar relación con opciones
            try:
                opciones_count = len(menu.opciones)
                print(f"      Opciones: {opciones_count}")
                
                for opcion_rel in menu.opciones[:3]:  # Solo las primeras 3
                    print(f"         - {opcion_rel.opcion.nombre} ({opcion_rel.opcion.tipo})")
                    
            except Exception as e:
                print(f"      ❌ Error en relación opciones: {str(e)}")
        
        print("✅ Prueba de relaciones completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de relaciones: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = test_model_relations()
    if success:
        print("\n🎉 Las relaciones del modelo funcionan correctamente")
    else:
        print("\n💥 Hay problemas con las relaciones del modelo")
        sys.exit(1)







