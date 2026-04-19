#!/usr/bin/env python3
"""
Script simple para crear la nueva tabla de menús
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database import get_database_url

def create_new_menus_table():
    """Crear la nueva tabla de menús"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        print("🔄 Creando nueva tabla de menús...")
        
        # Crear la tabla nueva
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS menus_dia_restructured (
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
            print("✅ Tabla 'menus_dia_restructured' creada exitosamente.")
            
            # Crear la tabla de opciones de menú si no existe
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS menu_dia_opciones (
                    id SERIAL PRIMARY KEY,
                    menu_dia_id INTEGER NOT NULL REFERENCES menus_dia_restructured(id) ON DELETE CASCADE,
                    opcion_id INTEGER NOT NULL REFERENCES opciones_platos(id) ON DELETE CASCADE,
                    disponible BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """))
            
            conn.commit()
            print("✅ Tabla 'menu_dia_opciones' creada exitosamente.")
            
    except Exception as e:
        print(f"❌ Error creando tabla: {str(e)}")
        raise

if __name__ == "__main__":
    create_new_menus_table()

