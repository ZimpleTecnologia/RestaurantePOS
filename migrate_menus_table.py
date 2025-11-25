#!/usr/bin/env python3
"""
Script para migrar datos de menus_dia a menus_dia_restructured
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_database_url

def migrate_menus_table():
    """Migrar datos de menus_dia a menus_dia_restructured"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            print("🔄 Iniciando migración de tabla de menús...")
            
            # Verificar si existe la tabla antigua
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'menus_dia'
                );
            """))
            tabla_antigua_existe = result.scalar()
            
            if not tabla_antigua_existe:
                print("✅ La tabla 'menus_dia' no existe, no hay datos que migrar.")
                return
            
            # Verificar si existe la tabla nueva
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'menus_dia_restructured'
                );
            """))
            tabla_nueva_existe = result.scalar()
            
            if not tabla_nueva_existe:
                print("📋 Creando tabla 'menus_dia_restructured'...")
                # Crear la tabla nueva usando SQLAlchemy
                from app.models.menu_restructured import MenuDiaRestructured
                MenuDiaRestructured.__table__.create(engine, checkfirst=True)
                print("✅ Tabla 'menus_dia_restructured' creada.")
            
            # Contar registros en la tabla antigua
            result = db.execute(text("SELECT COUNT(*) FROM menus_dia;"))
            count_antigua = result.scalar()
            print(f"📊 Registros en tabla antigua: {count_antigua}")
            
            # Contar registros en la tabla nueva
            result = db.execute(text("SELECT COUNT(*) FROM menus_dia_restructured;"))
            count_nueva = result.scalar()
            print(f"📊 Registros en tabla nueva: {count_nueva}")
            
            if count_antigua > 0 and count_nueva == 0:
                print("🔄 Migrando datos de 'menus_dia' a 'menus_dia_restructured'...")
                
                # Migrar datos
                db.execute(text("""
                    INSERT INTO menus_dia_restructured (id, fecha, nombre, descripcion, precio, estado, created_at, updated_at)
                    SELECT id, fecha, nombre, descripcion, precio, estado, created_at, updated_at
                    FROM menus_dia
                    ON CONFLICT (id) DO NOTHING;
                """))
                
                db.commit()
                print("✅ Datos migrados exitosamente.")
                
                # Verificar migración
                result = db.execute(text("SELECT COUNT(*) FROM menus_dia_restructured;"))
                count_final = result.scalar()
                print(f"📊 Registros migrados: {count_final}")
                
            elif count_nueva > 0:
                print("✅ La tabla nueva ya tiene datos, no se requiere migración.")
            else:
                print("✅ No hay datos que migrar.")
                
            print("🎉 Migración completada exitosamente.")
            
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_menus_table()

