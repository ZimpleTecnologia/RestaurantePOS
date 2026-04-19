#!/usr/bin/env python3
"""
Script para verificar las constraints de la tabla menu_dia_opciones
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings

def check_table_constraints():
    """Verificar las constraints de la tabla menu_dia_opciones"""
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        
        print("🔍 Verificando constraints de la tabla menu_dia_opciones...")
        
        with engine.connect() as conn:
            # Verificar si existe la tabla
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'menu_dia_opciones'
                );
            """))
            tabla_existe = result.scalar()
            
            if not tabla_existe:
                print("❌ La tabla 'menu_dia_opciones' no existe.")
                return
            
            print("✅ La tabla 'menu_dia_opciones' existe.")
            
            # Verificar foreign keys
            result = conn.execute(text("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'menu_dia_opciones';
            """))
            
            foreign_keys = result.fetchall()
            print(f"\n📋 Foreign keys encontradas: {len(foreign_keys)}")
            
            for fk in foreign_keys:
                print(f"   - {fk[0]}: {fk[2]} -> {fk[3]}.{fk[4]}")
            
            # Verificar si existe la tabla menus_dia_restructured
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'menus_dia_restructured'
                );
            """))
            tabla_nueva_existe = result.scalar()
            
            print(f"\n📊 Tabla 'menus_dia_restructured' existe: {tabla_nueva_existe}")
            
            if tabla_nueva_existe:
                # Contar registros en ambas tablas
                result = conn.execute(text("SELECT COUNT(*) FROM menus_dia;"))
                count_antigua = result.scalar()
                
                result = conn.execute(text("SELECT COUNT(*) FROM menus_dia_restructured;"))
                count_nueva = result.scalar()
                
                print(f"📊 Registros en 'menus_dia': {count_antigua}")
                print(f"📊 Registros en 'menus_dia_restructured': {count_nueva}")
            
    except Exception as e:
        print(f"❌ Error verificando constraints: {str(e)}")
        raise

if __name__ == "__main__":
    check_table_constraints()
