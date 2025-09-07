#!/usr/bin/env python3
"""
Script para corregir los valores del enum ProductCategory en la base de datos
"""
import os
import sys
from sqlalchemy import create_engine, text

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def fix_enum_values():
    """Corregir valores del enum ProductCategory"""
    print("🔧 Corrigiendo valores del enum ProductCategory...")
    
    # Crear engine
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Mapeo de valores incorrectos a correctos
        enum_mapping = {
            'otro': 'OTRO',
            'entrada': 'ENTRADA',
            'plato_principal': 'PLATO_PRINCIPAL',
            'postre': 'POSTRE',
            'bebida': 'BEBIDA',
            'alcohol': 'ALCOHOL',
            'ingrediente': 'INGREDIENTE',
            'utensilio': 'UTENSILIO'
        }
        
        # Verificar qué valores incorrectos existen
        result = conn.execute(text("""
            SELECT DISTINCT category 
            FROM products 
            WHERE category IS NOT NULL
        """))
        existing_values = [row[0] for row in result.fetchall()]
        
        print(f"📋 Valores encontrados en la base de datos: {existing_values}")
        
        # Corregir cada valor incorrecto
        for wrong_value, correct_value in enum_mapping.items():
            if wrong_value in existing_values:
                print(f"🔄 Corrigiendo '{wrong_value}' → '{correct_value}'...")
                result = conn.execute(text("""
                    UPDATE products 
                    SET category = :correct_value 
                    WHERE category = :wrong_value
                """), {"correct_value": correct_value, "wrong_value": wrong_value})
                print(f"   ✅ Corregidos {result.rowcount} registros")
        
        # Verificar valores después de la corrección
        result = conn.execute(text("""
            SELECT DISTINCT category 
            FROM products 
            WHERE category IS NOT NULL
        """))
        final_values = [row[0] for row in result.fetchall()]
        
        print(f"📋 Valores después de la corrección: {final_values}")
        
        conn.commit()
        print("✅ Valores del enum corregidos correctamente")

if __name__ == "__main__":
    fix_enum_values()
