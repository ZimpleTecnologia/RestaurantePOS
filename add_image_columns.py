#!/usr/bin/env python3
"""
Script para agregar columnas de imagen a la tabla opciones_platos
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings

def add_image_columns():
    """Agregar columnas de imagen a la tabla opciones_platos"""
    try:
        # Crear conexión a la base de datos
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # Verificar si las columnas ya existen
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'opciones_platos' 
                AND column_name IN ('imagen_data', 'imagen_tipo')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            # Agregar columna imagen_data si no existe
            if 'imagen_data' not in existing_columns:
                print("Agregando columna imagen_data...")
                conn.execute(text("ALTER TABLE opciones_platos ADD COLUMN imagen_data BYTEA"))
                print("✅ Columna imagen_data agregada")
            else:
                print("✅ Columna imagen_data ya existe")
            
            # Agregar columna imagen_tipo si no existe
            if 'imagen_tipo' not in existing_columns:
                print("Agregando columna imagen_tipo...")
                conn.execute(text("ALTER TABLE opciones_platos ADD COLUMN imagen_tipo VARCHAR(50)"))
                print("✅ Columna imagen_tipo agregada")
            else:
                print("✅ Columna imagen_tipo ya existe")
            
            conn.commit()
            print("🎉 Migración completada exitosamente")
            
    except Exception as e:
        print(f"❌ Error en la migración: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Iniciando migración para agregar columnas de imagen...")
    success = add_image_columns()
    if success:
        print("✅ Migración completada")
    else:
        print("❌ Migración falló")

