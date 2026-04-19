#!/usr/bin/env python3
"""
Script para corregir la foreign key constraint de menu_dia_opciones
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings

def fix_foreign_key_constraint():
    """Corregir la foreign key constraint de menu_dia_opciones"""
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        
        print("🔧 Corrigiendo foreign key constraint de menu_dia_opciones...")
        
        with engine.connect() as conn:
            # Verificar si existe la tabla menu_dia_opciones
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'menu_dia_opciones'
                );
            """))
            tabla_existe = result.scalar()
            
            if not tabla_existe:
                print("❌ La tabla 'menu_dia_opciones' no existe. Creándola...")
                
                # Crear la tabla con la foreign key correcta
                conn.execute(text("""
                    CREATE TABLE menu_dia_opciones (
                        id SERIAL PRIMARY KEY,
                        menu_dia_id INTEGER NOT NULL REFERENCES menus_dia_restructured(id) ON DELETE CASCADE,
                        opcion_id INTEGER NOT NULL REFERENCES opciones_platos(id) ON DELETE CASCADE,
                        disponible BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """))
                conn.commit()
                print("✅ Tabla 'menu_dia_opciones' creada con foreign key correcta.")
                return
            
            # Verificar si existe la tabla menus_dia_restructured
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'menus_dia_restructured'
                );
            """))
            tabla_nueva_existe = result.scalar()
            
            if not tabla_nueva_existe:
                print("❌ La tabla 'menus_dia_restructured' no existe. Creándola...")
                
                # Crear la tabla menus_dia_restructured
                conn.execute(text("""
                    CREATE TABLE menus_dia_restructured (
                        id SERIAL PRIMARY KEY,
                        fecha DATE NOT NULL UNIQUE,
                        nombre VARCHAR(100) NOT NULL,
                        descripcion TEXT,
                        precio NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
                        estado VARCHAR(50),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE
                    );
                """))
                conn.commit()
                print("✅ Tabla 'menus_dia_restructured' creada.")
            
            # Verificar foreign keys actuales
            result = conn.execute(text("""
                SELECT 
                    tc.constraint_name,
                    ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                JOIN information_schema.key_column_usage AS kcu
                    ON kcu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'menu_dia_opciones'
                    AND kcu.column_name = 'menu_dia_id';
            """))
            
            foreign_keys = result.fetchall()
            
            # Buscar la constraint que apunta a menus_dia
            constraint_to_drop = None
            for fk in foreign_keys:
                if fk[1] == 'menus_dia':
                    constraint_to_drop = fk[0]
                    break
            
            if constraint_to_drop:
                print(f"🔧 Eliminando constraint '{constraint_to_drop}' que apunta a 'menus_dia'...")
                
                # Eliminar la constraint antigua
                conn.execute(text(f"ALTER TABLE menu_dia_opciones DROP CONSTRAINT {constraint_to_drop};"))
                conn.commit()
                print("✅ Constraint antigua eliminada.")
                
                # Crear la nueva constraint que apunta a menus_dia_restructured
                conn.execute(text("""
                    ALTER TABLE menu_dia_opciones 
                    ADD CONSTRAINT menu_dia_opciones_menu_dia_id_fkey 
                    FOREIGN KEY (menu_dia_id) REFERENCES menus_dia_restructured(id) ON DELETE CASCADE;
                """))
                conn.commit()
                print("✅ Nueva constraint creada apuntando a 'menus_dia_restructured'.")
                
            else:
                print("✅ No se encontró constraint que apunte a 'menus_dia'.")
                
                # Verificar si ya apunta a menus_dia_restructured
                result = conn.execute(text("""
                    SELECT 
                        tc.constraint_name,
                        ccu.table_name AS foreign_table_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    JOIN information_schema.key_column_usage AS kcu
                        ON kcu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name = 'menu_dia_opciones'
                        AND kcu.column_name = 'menu_dia_id'
                        AND ccu.table_name = 'menus_dia_restructured';
                """))
                
                if result.fetchall():
                    print("✅ La constraint ya apunta a 'menus_dia_restructured'.")
                else:
                    print("⚠️ No se encontró constraint para menu_dia_id. Creando una nueva...")
                    
                    # Crear la constraint
                    conn.execute(text("""
                        ALTER TABLE menu_dia_opciones 
                        ADD CONSTRAINT menu_dia_opciones_menu_dia_id_fkey 
                        FOREIGN KEY (menu_dia_id) REFERENCES menus_dia_restructured(id) ON DELETE CASCADE;
                    """))
                    conn.commit()
                    print("✅ Constraint creada.")
            
            print("🎉 Foreign key constraint corregida exitosamente.")
            
    except Exception as e:
        print(f"❌ Error corrigiendo constraint: {str(e)}")
        raise

if __name__ == "__main__":
    fix_foreign_key_constraint()
