#!/usr/bin/env python3
"""
Script para verificar la estructura actual de la tabla tables
"""
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text

def verificar_estructura_tabla():
    """Verificar la estructura actual de la tabla tables"""
    db = SessionLocal()
    
    try:
        print("🔍 Verificando estructura de la tabla 'tables'...")
        
        # Obtener todas las columnas de la tabla
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'restaurant_tables'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        
        print("\n📋 Estructura actual de la tabla 'tables':")
        print("-" * 80)
        for col in columns:
            print(f"  {col[0]:<20} {col[1]:<15} {'NULL' if col[2] == 'YES' else 'NOT NULL':<10} {col[3] or ''}")
        
        # Verificar si hay datos en la tabla
        result = db.execute(text("SELECT COUNT(*) FROM restaurant_tables"))
        count = result.fetchone()[0]
        print(f"\n📊 Registros en la tabla: {count}")
        
        if count > 0:
            print("\n📄 Primeros registros:")
            result = db.execute(text("SELECT * FROM restaurant_tables LIMIT 3"))
            rows = result.fetchall()
            for row in rows:
                print(f"  {row}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    verificar_estructura_tabla()
