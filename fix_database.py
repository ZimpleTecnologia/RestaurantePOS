#!/usr/bin/env python3
"""
Script para agregar las columnas faltantes en la tabla products
"""
import os
import sys
from sqlalchemy import create_engine, text

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def fix_database():
    """Agregar columnas faltantes en la tabla products"""
    print("🔧 Arreglando base de datos...")
    
    # Crear engine
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Verificar qué columnas existen
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND table_schema = 'public'
        """))
        existing_columns = [row[0] for row in result.fetchall()]
        
        print(f"📋 Columnas existentes: {existing_columns}")
        
        # Columnas que necesitamos agregar
        columns_to_add = [
            ("barcode", "VARCHAR(50)"),
            ("sku", "VARCHAR(50)"),
            ("category", "VARCHAR(50) DEFAULT 'otro'"),
            ("subcategory", "VARCHAR(50)"),
            ("track_stock", "BOOLEAN DEFAULT FALSE"),
            ("stock_quantity", "INTEGER DEFAULT 0"),
            ("min_stock_level", "INTEGER DEFAULT 0"),
            ("max_stock_level", "INTEGER DEFAULT 0"),
            ("reorder_point", "INTEGER DEFAULT 0"),
            ("unit", "VARCHAR(20) DEFAULT 'unidad'"),
            ("weight", "NUMERIC(8,3)"),
            ("volume", "NUMERIC(8,3)"),
            ("is_featured", "BOOLEAN DEFAULT FALSE"),
            ("calories", "INTEGER"),
            ("protein", "NUMERIC(5,2)"),
            ("carbs", "NUMERIC(5,2)"),
            ("fat", "NUMERIC(5,2)")
        ]
        
        # Agregar columnas faltantes
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                print(f"➕ Agregando columna '{column_name}'...")
                try:
                    conn.execute(text(f"ALTER TABLE products ADD COLUMN {column_name} {column_type}"))
                    print(f"   ✅ Columna '{column_name}' agregada")
                except Exception as e:
                    print(f"   ⚠️ Error agregando columna '{column_name}': {e}")
            else:
                print(f"   ✅ Columna '{column_name}' ya existe")
        
        # Verificar si las columnas de stock existen
        if 'stock' not in existing_columns:
            print("➕ Agregando columna 'stock'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 0"))
        
        if 'min_stock' not in existing_columns:
            print("➕ Agregando columna 'min_stock'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN min_stock INTEGER DEFAULT 0"))
        
        if 'max_stock' not in existing_columns:
            print("➕ Agregando columna 'max_stock'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN max_stock INTEGER DEFAULT 100"))
        
        if 'image_url' not in existing_columns:
            print("➕ Agregando columna 'image_url'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(255)"))
        
        if 'supplier_id' not in existing_columns:
            print("➕ Agregando columna 'supplier_id'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN supplier_id INTEGER"))
        
        conn.commit()
        print("✅ Base de datos arreglada correctamente")

if __name__ == "__main__":
    fix_database()
