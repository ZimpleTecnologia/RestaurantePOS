#!/usr/bin/env python3
"""
Script para verificar las tablas existentes en la base de datos
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verificar_tablas():
    """Verificar qué tablas existen en la base de datos"""
    try:
        # Configurar conexión a la base de datos
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/restaurante_pos")
        engine = create_engine(database_url)
        
        print("🔍 Verificando tablas en la base de datos...")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Listar todas las tablas
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)).fetchall()
            
            print(f"📋 Tablas encontradas ({len(result)}):")
            for row in result:
                print(f"   - {row[0]}")
            
            print("\n" + "=" * 50)
            
            # Verificar si existe inventory_movements
            if any(row[0] == 'inventory_movements' for row in result):
                print("✅ Tabla 'inventory_movements' existe")
                
                # Verificar estructura de la tabla
                columns = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'inventory_movements'
                    ORDER BY ordinal_position
                """)).fetchall()
                
                print("\n📋 Estructura de inventory_movements:")
                for col in columns:
                    print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            else:
                print("❌ Tabla 'inventory_movements' NO existe")
                
                # Verificar si existe alguna tabla relacionada con inventario
                inventory_tables = [row[0] for row in result if 'inventory' in row[0].lower()]
                if inventory_tables:
                    print(f"\n📋 Tablas relacionadas con inventario encontradas:")
                    for table in inventory_tables:
                        print(f"   - {table}")
                else:
                    print("\n❌ No se encontraron tablas relacionadas con inventario")
            
            print("\n" + "=" * 50)
            
            # Verificar si existe la tabla products
            if any(row[0] == 'products' for row in result):
                print("✅ Tabla 'products' existe")
                
                # Verificar si tiene las columnas necesarias
                product_columns = conn.execute(text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns 
                    WHERE table_name = 'products'
                    AND column_name IN ('product_type', 'purchase_price', 'stock_quantity')
                    ORDER BY column_name
                """)).fetchall()
                
                print("\n📋 Columnas de inventario en products:")
                for col in product_columns:
                    print(f"   - {col[0]}: {col[1]}")
                    
                missing_columns = []
                expected_columns = ['product_type', 'purchase_price', 'stock_quantity']
                existing_columns = [col[0] for col in product_columns]
                
                for col in expected_columns:
                    if col not in existing_columns:
                        missing_columns.append(col)
                
                if missing_columns:
                    print(f"\n❌ Columnas faltantes: {', '.join(missing_columns)}")
                else:
                    print("\n✅ Todas las columnas de inventario están presentes")
            else:
                print("❌ Tabla 'products' NO existe")
                
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")

if __name__ == "__main__":
    verificar_tablas()
