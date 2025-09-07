#!/usr/bin/env python3
"""
Script para verificar productos de inventario
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verificar_productos():
    """Verificar productos de inventario"""
    try:
        # Configurar conexión a la base de datos
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/restaurante_pos")
        engine = create_engine(database_url)
        
        print("🔍 Verificando productos de inventario...")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Verificar productos de inventario
            result = conn.execute(text("""
                SELECT id, name, product_type, stock_quantity, min_stock_level, unit, is_active
                FROM products 
                WHERE product_type = 'INVENTORY' AND is_active = true
                ORDER BY id
            """)).fetchall()
            
            print(f"📦 Productos de inventario encontrados: {len(result)}")
            for row in result:
                print(f"   ID: {row[0]}, Nombre: {row[1]}, Tipo: {row[2]}, Stock: {row[3]}, Mín: {row[4]}, Unidad: {row[5]}")
            
            # Verificar categorías
            result = conn.execute(text("""
                SELECT id, name, is_active
                FROM categories 
                WHERE is_active = true
                ORDER BY id
            """)).fetchall()
            
            print(f"\n📂 Categorías encontradas: {len(result)}")
            for row in result:
                print(f"   ID: {row[0]}, Nombre: {row[1]}, Activa: {row[2]}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_productos()
