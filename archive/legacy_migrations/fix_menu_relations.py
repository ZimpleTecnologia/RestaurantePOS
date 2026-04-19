#!/usr/bin/env python3
"""
Script para corregir las relaciones entre tablas de menús
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database import engine

def fix_menu_relations():
    """Corregir las relaciones entre tablas de menús"""
    try:
        # Usar el engine existente
        print("🔧 Corrigiendo relaciones entre tablas de menús...")
        
        with engine.connect() as conn:
            # 1. Verificar estructura de la tabla menus_dia
            print("\n1. 📋 Verificando tabla menus_dia...")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'menus_dia' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("   Columnas encontradas:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]}) - Nullable: {col[2]}")
            
            # 2. Verificar estructura de la tabla menu_dia_opciones
            print("\n2. 🔗 Verificando tabla menu_dia_opciones...")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'menu_dia_opciones' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("   Columnas encontradas:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]}) - Nullable: {col[2]}")
            
            # 3. Verificar claves foráneas existentes
            print("\n3. 🔑 Verificando claves foráneas...")
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
                    AND (tc.table_name = 'menu_dia_opciones' OR tc.table_name = 'menus_dia')
                ORDER BY tc.table_name, kcu.column_name
            """))
            
            fks = result.fetchall()
            print("   Claves foráneas encontradas:")
            for fk in fks:
                print(f"   - {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]} ({fk[0]})")
            
            # 4. Verificar datos existentes
            print("\n4. 📊 Verificando datos existentes...")
            
            # Contar menús
            result = conn.execute(text("SELECT COUNT(*) FROM menus_dia"))
            menu_count = result.scalar()
            print(f"   Menús existentes: {menu_count}")
            
            # Contar opciones de menú
            result = conn.execute(text("SELECT COUNT(*) FROM menu_dia_opciones"))
            opciones_count = result.scalar()
            print(f"   Opciones de menú existentes: {opciones_count}")
            
            # 5. Verificar si hay inconsistencias
            print("\n5. 🔍 Verificando inconsistencias...")
            
            # Opciones sin menú válido
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM menu_dia_opciones mdo 
                LEFT JOIN menus_dia md ON mdo.menu_dia_id = md.id 
                WHERE md.id IS NULL
            """))
            orphaned_opciones = result.scalar()
            print(f"   Opciones huérfanas: {orphaned_opciones}")
            
            # 6. Proponer solución
            print("\n6. 💡 Solución propuesta:")
            
            if orphaned_opciones > 0:
                print("   ❌ Se encontraron opciones huérfanas. Limpiando...")
                conn.execute(text("""
                    DELETE FROM menu_dia_opciones 
                    WHERE menu_dia_id NOT IN (SELECT id FROM menus_dia)
                """))
                conn.commit()
                print("   ✅ Opciones huérfanas eliminadas")
            
            # 7. Verificar que las relaciones funcionen
            print("\n7. ✅ Verificando relaciones...")
            
            # Probar una consulta simple
            result = conn.execute(text("""
                SELECT md.id, md.nombre, COUNT(mdo.id) as opciones_count
                FROM menus_dia md
                LEFT JOIN menu_dia_opciones mdo ON md.id = mdo.menu_dia_id
                GROUP BY md.id, md.nombre
                LIMIT 5
            """))
            
            menus_with_opciones = result.fetchall()
            print("   Menús con sus opciones:")
            for menu in menus_with_opciones:
                print(f"   - {menu[1]} (ID: {menu[0]}) - {menu[2]} opciones")
            
            print("\n🎉 Verificación completada exitosamente!")
            
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Script de Corrección de Relaciones de Menús")
    print("=" * 50)
    
    success = fix_menu_relations()
    
    if success:
        print("\n✅ Script ejecutado exitosamente!")
        print("   Las relaciones entre tablas han sido verificadas y corregidas.")
    else:
        print("\n❌ Error durante la ejecución del script.")
        sys.exit(1)