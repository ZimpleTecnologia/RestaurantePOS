#!/usr/bin/env python3
"""
Script para actualizar la base de datos con los nuevos campos de productos
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import get_db
from app.models import Product, Category, SubCategory

def update_database():
    """Actualizar la base de datos con los nuevos campos"""
    print("🔄 Actualizando base de datos...")
    
    # Crear engine
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Verificar si las columnas ya existen
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products'
        """))
        columns = [row[0] for row in result.fetchall()]
        
        # Agregar columnas si no existen
        if 'code' not in columns:
            print("➕ Agregando columna 'code'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN code VARCHAR(50)"))
        
        if 'stock' not in columns:
            print("➕ Agregando columna 'stock'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 0"))
        
        if 'min_stock' not in columns:
            print("➕ Agregando columna 'min_stock'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN min_stock INTEGER DEFAULT 0"))
        
        if 'max_stock' not in columns:
            print("➕ Agregando columna 'max_stock'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN max_stock INTEGER DEFAULT 100"))
        
        if 'image_url' not in columns:
            print("➕ Agregando columna 'image_url'...")
            conn.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(255)"))
        
        # Crear tablas de categorías si no existen
        print("📋 Verificando tablas de categorías...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS subcategories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                category_id INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        """))
        
        # Insertar categorías por defecto si no existen
        result = conn.execute(text("SELECT COUNT(*) FROM categories"))
        if result.fetchone()[0] == 0:
            print("📝 Insertando categorías por defecto...")
            default_categories = [
                ("Bebidas", "Bebidas y refrescos"),
                ("Platos Principales", "Platos principales del menú"),
                ("Entradas", "Entradas y aperitivos"),
                ("Postres", "Postres y dulces"),
                ("Ingredientes", "Ingredientes para cocina"),
                ("Otros", "Otros productos")
            ]
            
            for name, description in default_categories:
                conn.execute(text("""
                    INSERT INTO categories (name, description) 
                    VALUES (:name, :description)
                """), {"name": name, "description": description})
        
        conn.commit()
        print("✅ Base de datos actualizada correctamente")

if __name__ == "__main__":
    update_database()
