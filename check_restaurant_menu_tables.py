#!/usr/bin/env python3
"""
Script para verificar si las tablas del sistema de menús del restaurante existen
"""
import sys
import os
from sqlalchemy import create_engine, text, inspect
from app.config import settings

def check_restaurant_menu_tables():
    """Verificar si las tablas del sistema de menús del restaurante existen"""
    print("🔍 Verificando tablas del sistema de menús del restaurante...")
    print("=" * 70)
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # Verificar si las tablas existen
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            print(f"📊 Total de tablas en la base de datos: {len(existing_tables)}")
            print(f"📋 Tablas existentes: {sorted(existing_tables)}")
            
            # Tablas que deberían existir para el sistema de menús del restaurante
            required_tables = [
                'categorias_menu',
                'platos_restaurante', 
                'menus_dia',
                'menu_categoria_plato',
                'acompanamientos_fijos'
            ]
            
            print(f"\n🎯 Tablas requeridas para el sistema de menús:")
            missing_tables = []
            
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ {table} - EXISTE")
                    
                    # Contar registros en la tabla
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        print(f"   📊 Registros: {count}")
                    except Exception as e:
                        print(f"   ❌ Error contando registros: {e}")
                else:
                    print(f"❌ {table} - NO EXISTE")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"\n❌ Faltan {len(missing_tables)} tablas:")
                for table in missing_tables:
                    print(f"   - {table}")
                print(f"\n💡 Solución: Ejecutar el script de creación de tablas")
                print(f"   python create_tables_simple.py")
            else:
                print(f"\n✅ Todas las tablas requeridas existen")
                
                # Verificar datos de ejemplo
                print(f"\n📋 Verificando datos de ejemplo...")
                try:
                    # Verificar categorías
                    result = conn.execute(text("SELECT COUNT(*) FROM categorias_menu"))
                    categorias_count = result.scalar()
                    print(f"   📊 Categorías: {categorias_count}")
                    
                    # Verificar platos
                    result = conn.execute(text("SELECT COUNT(*) FROM platos_restaurante"))
                    platos_count = result.scalar()
                    print(f"   📊 Platos: {platos_count}")
                    
                    # Verificar menús
                    result = conn.execute(text("SELECT COUNT(*) FROM menus_dia"))
                    menus_count = result.scalar()
                    print(f"   📊 Menús: {menus_count}")
                    
                    # Verificar acompañamientos
                    result = conn.execute(text("SELECT COUNT(*) FROM acompanamientos_fijos"))
                    acompanamientos_count = result.scalar()
                    print(f"   📊 Acompañamientos: {acompanamientos_count}")
                    
                    if categorias_count == 0 and platos_count == 0:
                        print(f"\n⚠️ Las tablas existen pero no tienen datos")
                        print(f"💡 Solución: Ejecutar el script de datos de ejemplo")
                        print(f"   python create_tables_simple.py")
                    
                except Exception as e:
                    print(f"❌ Error verificando datos: {e}")
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        print(f"💡 Verifica que el servidor de base de datos esté ejecutándose")

if __name__ == "__main__":
    check_restaurant_menu_tables()


