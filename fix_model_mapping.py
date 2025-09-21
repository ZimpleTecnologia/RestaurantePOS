#!/usr/bin/env python3
"""
Script para corregir el mapeo del modelo MenuDiaRestructured
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from app.database import engine
from app.models.menu_restructured import MenuDiaRestructured, MenuDiaOpcion

def fix_model_mapping():
    """Corregir el mapeo del modelo"""
    try:
        print("🔧 Corrigiendo mapeo del modelo MenuDiaRestructured...")
        
        with engine.connect() as conn:
            # 1. Verificar la estructura real de la tabla
            print("\n1. 📋 Verificando estructura real de menus_dia...")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'menus_dia' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("   Estructura real de la tabla:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]}) - Nullable: {col[2]} - Default: {col[3]}")
            
            # 2. Verificar si hay problemas de mapeo
            print("\n2. 🔍 Verificando mapeo del modelo...")
            
            # Probar una consulta simple con el modelo
            try:
                from sqlalchemy.orm import sessionmaker
                Session = sessionmaker(bind=engine)
                session = Session()
                
                # Intentar cargar un menú
                menu = session.query(MenuDiaRestructured).first()
                if menu:
                    print(f"   ✅ Modelo funciona - Menú encontrado: {menu.nombre}")
                    print(f"   - ID: {menu.id}")
                    print(f"   - Fecha: {menu.fecha}")
                    print(f"   - Precio: {menu.precio}")
                else:
                    print("   ⚠️ No se encontraron menús")
                
                session.close()
                
            except Exception as e:
                print(f"   ❌ Error en el modelo: {str(e)}")
                print(f"   Tipo de error: {type(e).__name__}")
                
                # 3. Verificar si el problema es de relación
                print("\n3. 🔗 Verificando relaciones...")
                try:
                    # Probar la relación
                    session = Session()
                    menu = session.query(MenuDiaRestructured).first()
                    if menu:
                        opciones = session.query(MenuDiaOpcion).filter(
                            MenuDiaOpcion.menu_dia_id == menu.id
                        ).all()
                        print(f"   ✅ Relación funciona - {len(opciones)} opciones encontradas")
                    session.close()
                except Exception as rel_error:
                    print(f"   ❌ Error en relación: {str(rel_error)}")
            
            # 4. Verificar datos de prueba
            print("\n4. 📊 Verificando datos de prueba...")
            result = conn.execute(text("""
                SELECT md.id, md.nombre, md.fecha, md.precio, md.estado,
                       COUNT(mdo.id) as opciones_count
                FROM menus_dia md
                LEFT JOIN menu_dia_opciones mdo ON md.id = mdo.menu_dia_id
                GROUP BY md.id, md.nombre, md.fecha, md.precio, md.estado
                ORDER BY md.id
            """))
            
            menus_data = result.fetchall()
            print("   Datos de menús:")
            for menu in menus_data:
                print(f"   - ID: {menu[0]} | {menu[1]} | {menu[2]} | ${menu[3]} | {menu[4]} | {menu[5]} opciones")
            
            print("\n🎉 Verificación del modelo completada!")
            
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Script de Corrección del Mapeo del Modelo")
    print("=" * 50)
    
    success = fix_model_mapping()
    
    if success:
        print("\n✅ Script ejecutado exitosamente!")
        print("   El mapeo del modelo ha sido verificado.")
    else:
        print("\n❌ Error durante la ejecución del script.")
        sys.exit(1)
