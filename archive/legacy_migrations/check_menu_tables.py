#!/usr/bin/env python3
"""
Script para verificar las tablas de menús en la base de datos
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def check_menu_tables():
    """Verificar las tablas de menús en la base de datos"""
    print("🔍 Verificando tablas de menús en la base de datos...")
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar si existen las tablas
        print("\n📋 Verificando tablas de menús...")
        
        # Verificar tabla platos
        try:
            result = session.execute(text("SELECT COUNT(*) FROM platos"))
            count = result.fetchone()[0]
            print(f"✅ Tabla 'platos' existe: {count} registros")
        except Exception as e:
            print(f"❌ Tabla 'platos' no existe: {e}")
        
        # Verificar tabla menus
        try:
            result = session.execute(text("SELECT COUNT(*) FROM menus"))
            count = result.fetchone()[0]
            print(f"✅ Tabla 'menus' existe: {count} registros")
        except Exception as e:
            print(f"❌ Tabla 'menus' no existe: {e}")
        
        # Verificar tabla menu_platos
        try:
            result = session.execute(text("SELECT COUNT(*) FROM menu_platos"))
            count = result.fetchone()[0]
            print(f"✅ Tabla 'menu_platos' existe: {count} registros")
        except Exception as e:
            print(f"❌ Tabla 'menu_platos' no existe: {e}")
        
        # Verificar estructura de la tabla platos
        print("\n🔍 Verificando estructura de la tabla 'platos'...")
        try:
            result = session.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'platos'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            if columns:
                print("✅ Estructura de la tabla 'platos':")
                for col in columns:
                    print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            else:
                print("❌ No se encontraron columnas en la tabla 'platos'")
        except Exception as e:
            print(f"❌ Error verificando estructura de 'platos': {e}")
        
        # Verificar estructura de la tabla menus
        print("\n🔍 Verificando estructura de la tabla 'menus'...")
        try:
            result = session.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'menus'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            if columns:
                print("✅ Estructura de la tabla 'menus':")
                for col in columns:
                    print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            else:
                print("❌ No se encontraron columnas en la tabla 'menus'")
        except Exception as e:
            print(f"❌ Error verificando estructura de 'menus': {e}")
        
        # Verificar datos de ejemplo
        print("\n📊 Verificando datos de ejemplo...")
        try:
            result = session.execute(text("SELECT * FROM platos LIMIT 3"))
            platos = result.fetchall()
            if platos:
                print(f"✅ Datos de ejemplo en 'platos': {len(platos)} registros")
                for plato in platos:
                    print(f"   - ID: {plato[0]}, Nombre: {plato[1]}, Precio: {plato[3]}")
            else:
                print("⚠️ No hay datos en la tabla 'platos'")
        except Exception as e:
            print(f"❌ Error verificando datos de 'platos': {e}")
        
        session.close()
        print("\n🎉 Verificación de tablas completada!")
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")

if __name__ == "__main__":
    check_menu_tables()