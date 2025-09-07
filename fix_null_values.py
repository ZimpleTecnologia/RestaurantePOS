#!/usr/bin/env python3
"""
Script para corregir valores NULL en la base de datos
"""
import os
import sys
from sqlalchemy import create_engine, text

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def fix_null_values():
    """Corregir valores NULL en la base de datos"""
    print("🔧 Corrigiendo valores NULL en la base de datos...")
    
    # Crear engine
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Actualizar valores NULL con valores por defecto
        updates = [
            ("min_stock", "0"),
            ("max_stock", "100"),
            ("stock", "0"),
            ("cost_price", "0.00"),
            ("track_stock", "FALSE"),
            ("stock_quantity", "0"),
            ("min_stock_level", "0"),
            ("max_stock_level", "0"),
            ("reorder_point", "0"),
            ("unit", "'unidad'"),
            ("is_featured", "FALSE"),
            ("is_active", "TRUE")
        ]
        
        for column, default_value in updates:
            print(f"🔄 Actualizando {column} con valor por defecto {default_value}...")
            result = conn.execute(text(f"""
                UPDATE products 
                SET {column} = {default_value} 
                WHERE {column} IS NULL
            """))
            print(f"   ✅ Actualizados {result.rowcount} registros")
        
        conn.commit()
        print("✅ Valores NULL corregidos correctamente")

if __name__ == "__main__":
    fix_null_values()

