#!/usr/bin/env python3
"""
Script para revisar las restricciones de la base de datos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from sqlalchemy import text

def check_constraints():
    """Revisar restricciones de la base de datos"""
    print("🔍 Revisando restricciones de la base de datos...")
    
    try:
        db = next(get_db())
        
        # Verificar estructura de la tabla
        print("\n📋 Estructura de la tabla carta_restaurante:")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'carta_restaurante' 
            ORDER BY ordinal_position
        """)).fetchall()
        
        for row in result:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        # Verificar restricciones de verificación
        print("\n🔒 Restricciones de verificación:")
        result = db.execute(text("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint 
            WHERE conrelid = 'carta_restaurante'::regclass 
            AND contype = 'c'
        """)).fetchall()
        
        for row in result:
            print(f"  {row[0]}: {row[1]}")
        
        # Verificar si hay datos existentes
        print("\n📊 Datos existentes en carta_restaurante:")
        result = db.execute(text("SELECT COUNT(*) FROM carta_restaurante")).fetchone()
        print(f"  Total registros: {result[0]}")
        
        if result[0] > 0:
            result = db.execute(text("SELECT DISTINCT categoria FROM carta_restaurante WHERE categoria IS NOT NULL")).fetchall()
            print("  Categorías existentes:")
            for row in result:
                print(f"    - '{row[0]}'")
        
        # Verificar si hay un enum definido
        print("\n🏷️ Enums definidos:")
        result = db.execute(text("""
            SELECT t.typname, e.enumlabel
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            WHERE t.typname LIKE '%categoria%' OR t.typname LIKE '%plato%'
            ORDER BY t.typname, e.enumsortorder
        """)).fetchall()
        
        if result:
            current_enum = None
            for row in result:
                if row[0] != current_enum:
                    print(f"  {row[0]}:")
                    current_enum = row[0]
                print(f"    - '{row[1]}'")
        else:
            print("  No se encontraron enums relacionados con categorías")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_constraints()


