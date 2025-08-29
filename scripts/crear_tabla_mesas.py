#!/usr/bin/env python3
"""
Script para crear la tabla de mesas
"""
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text

def crear_tabla_mesas():
    """Crear la tabla de mesas"""
    db = SessionLocal()
    
    try:
        print("🏗️ Creando tabla restaurant_tables...")
        
        # Crear la tabla
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS restaurant_tables (
                id SERIAL PRIMARY KEY,
                table_number VARCHAR(10) UNIQUE NOT NULL,
                name VARCHAR(50) NOT NULL,
                capacity INTEGER NOT NULL DEFAULT 4,
                status VARCHAR(20) DEFAULT 'disponible',
                location VARCHAR(50),
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        
        # Crear índice único
        db.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ix_restaurant_tables_table_number 
            ON restaurant_tables (table_number)
        """))
        
        db.commit()
        print("✅ Tabla restaurant_tables creada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    crear_tabla_mesas()
