#!/usr/bin/env python3
"""
Script para probar directamente la base de datos y identificar el problema
"""
import sys
import os
from sqlalchemy import create_engine, text
from app.config import settings

def test_database_direct():
    """Probar directamente la base de datos para identificar el problema"""
    print("🔍 Probando base de datos directamente...")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            print("✅ Conexión a la base de datos exitosa")
            
            # Probar consulta de categorías
            print("\n📋 Probando consulta de categorías...")
            try:
                result = conn.execute(text("""
                    SELECT id, nombre, descripcion, orden, is_active, created_at, updated_at
                    FROM categorias_menu 
                    ORDER BY orden, nombre
                    LIMIT 5
                """))
                
                categorias = result.fetchall()
                print(f"✅ Consulta exitosa - {len(categorias)} categorías encontradas")
                
                for categoria in categorias:
                    print(f"   - ID: {categoria[0]}, Nombre: {categoria[1]}, Activo: {categoria[4]}")
                    
            except Exception as e:
                print(f"❌ Error en consulta de categorías: {e}")
                return False
            
            # Probar consulta de platos
            print("\n🍽️ Probando consulta de platos...")
            try:
                result = conn.execute(text("""
                    SELECT id, nombre, descripcion, precio, tipo, activo
                    FROM platos_restaurante 
                    WHERE activo = true
                    ORDER BY nombre
                    LIMIT 5
                """))
                
                platos = result.fetchall()
                print(f"✅ Consulta exitosa - {len(platos)} platos encontrados")
                
                for plato in platos:
                    print(f"   - ID: {plato[0]}, Nombre: {plato[1]}, Precio: ${plato[3]}, Tipo: {plato[4]}")
                    
            except Exception as e:
                print(f"❌ Error en consulta de platos: {e}")
                return False
            
            # Probar consulta de acompañamientos
            print("\n🥗 Probando consulta de acompañamientos...")
            try:
                result = conn.execute(text("""
                    SELECT id, nombre, descripcion, activo, orden
                    FROM acompanamientos_fijos 
                    WHERE activo = true
                    ORDER BY orden, nombre
                    LIMIT 5
                """))
                
                acompanamientos = result.fetchall()
                print(f"✅ Consulta exitosa - {len(acompanamientos)} acompañamientos encontrados")
                
                for acompanamiento in acompanamientos:
                    print(f"   - ID: {acompanamiento[0]}, Nombre: {acompanamiento[1]}")
                    
            except Exception as e:
                print(f"❌ Error en consulta de acompañamientos: {e}")
                return False
            
            # Probar consulta de menús
            print("\n📅 Probando consulta de menús...")
            try:
                result = conn.execute(text("""
                    SELECT menu_id, fecha, nombre, precio, estado, descripcion
                    FROM menus_dia 
                    ORDER BY fecha DESC
                    LIMIT 5
                """))
                
                menus = result.fetchall()
                print(f"✅ Consulta exitosa - {len(menus)} menús encontrados")
                
                for menu in menus:
                    print(f"   - ID: {menu[0]}, Fecha: {menu[1]}, Nombre: {menu[2]}, Estado: {menu[4]}")
                    
            except Exception as e:
                print(f"❌ Error en consulta de menús: {e}")
                return False
            
            print("\n🎉 Todas las consultas de base de datos funcionan correctamente")
            print("💡 El problema está en el código del router o en las relaciones SQLAlchemy")
            
            return True
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False

if __name__ == "__main__":
    success = test_database_direct()
    if success:
        print("\n✅ Base de datos funcionando correctamente")
        print("🔍 El problema está en el código del router")
    else:
        print("\n❌ Hay problemas en la base de datos")


