#!/usr/bin/env python3
"""
Script para migrar la tabla de mesas existente
"""
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from sqlalchemy import text

def migrar_tabla_mesas():
    """Migrar la tabla de mesas existente"""
    db = SessionLocal()
    
    try:
        print("🔄 Migrando tabla de mesas...")
        
        # Verificar si la tabla restaurant_tables existe
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'restaurant_tables'
        """))
        
        if result.fetchone():
            print("✅ La tabla restaurant_tables ya existe")
        else:
            print("➕ Creando tabla restaurant_tables...")
            db.execute(text("""
                CREATE TABLE restaurant_tables (
                    id SERIAL PRIMARY KEY,
                    table_number VARCHAR(10) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    capacity INTEGER NOT NULL DEFAULT 4,
                    status tablestatus DEFAULT 'disponible',
                    location VARCHAR(50),
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✅ Tabla restaurant_tables creada exitosamente")
        
        # Verificar si la columna table_number existe
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'restaurant_tables' AND column_name = 'table_number'
        """))
        
        if result.fetchone():
            print("✅ La columna table_number ya existe")
        else:
            print("➕ Agregando columna table_number...")
            db.execute(text("ALTER TABLE restaurant_tables ADD COLUMN table_number VARCHAR(10)"))
            db.execute(text("CREATE UNIQUE INDEX ix_restaurant_tables_table_number ON restaurant_tables (table_number)"))
            
            # Actualizar registros existentes
            db.execute(text("""
                UPDATE restaurant_tables 
                SET table_number = 'M' || id::text 
                WHERE table_number IS NULL
            """))
            
            # Hacer la columna NOT NULL
            db.execute(text("ALTER TABLE restaurant_tables ALTER COLUMN table_number SET NOT NULL"))
            
            print("✅ Columna table_number agregada exitosamente")
        
        # Verificar si la columna location existe
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'restaurant_tables' AND column_name = 'location'
        """))
        
        if result.fetchone():
            print("✅ La columna location ya existe")
        else:
            print("➕ Agregando columna location...")
            db.execute(text("ALTER TABLE restaurant_tables ADD COLUMN location VARCHAR(50)"))
            print("✅ Columna location agregada exitosamente")
        
        # Verificar si la columna description existe
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'restaurant_tables' AND column_name = 'description'
        """))
        
        if result.fetchone():
            print("✅ La columna description ya existe")
        else:
            print("➕ Agregando columna description...")
            db.execute(text("ALTER TABLE restaurant_tables ADD COLUMN description TEXT"))
            print("✅ Columna description agregada exitosamente")
        
        # Actualizar el enum de status si es necesario
        print("🔄 Actualizando enum de status...")
        try:
            db.execute(text("ALTER TYPE tablestatus RENAME TO tablestatus_old"))
        except:
            pass  # Si no existe, continuamos
        
        try:
            db.execute(text("""
                CREATE TYPE tablestatus AS ENUM (
                    'disponible', 'ocupada', 'reservada', 'limpieza', 'fuera_de_servicio'
                )
            """))
        except:
            pass  # Si ya existe, continuamos
        
        # Actualizar la columna status
        try:
            db.execute(text("""
                ALTER TABLE restaurant_tables 
                ALTER COLUMN status TYPE tablestatus 
                USING status::text::tablestatus
            """))
        except:
            print("⚠️  No se pudo actualizar el enum de status, pero continuamos...")
        
        db.commit()
        print("🎉 Migración completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrar_tabla_mesas()
