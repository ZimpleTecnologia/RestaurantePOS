#!/usr/bin/env python3
"""
Script para verificar y poblar la base de datos con productos de prueba
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

def check_database():
    """Verificar el estado de la base de datos"""
    print("🔍 Verificando base de datos...")
    
    # Crear engine
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Verificar si las tablas existen
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('products', 'categories', 'subcategories')
        """))
        tables = [row[0] for row in result.fetchall()]
        
        print(f"📋 Tablas encontradas: {tables}")
        
        # Verificar productos
        if 'products' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM products"))
            product_count = result.fetchone()[0]
            print(f"📦 Productos en la base de datos: {product_count}")
            
            if product_count > 0:
                result = conn.execute(text("SELECT id, name, code, price FROM products LIMIT 5"))
                products = result.fetchall()
                print("📋 Primeros productos:")
                for product in products:
                    print(f"   - ID: {product[0]}, Nombre: {product[1]}, Código: {product[2]}, Precio: {product[3]}")
        
        # Verificar categorías
        if 'categories' in tables:
            result = conn.execute(text("SELECT COUNT(*) FROM categories"))
            category_count = result.fetchone()[0]
            print(f"🏷️ Categorías en la base de datos: {category_count}")
            
            if category_count > 0:
                result = conn.execute(text("SELECT id, name FROM categories"))
                categories = result.fetchall()
                print("📋 Categorías disponibles:")
                for category in categories:
                    print(f"   - ID: {category[0]}, Nombre: {category[1]}")

def add_sample_products():
    """Agregar productos de muestra"""
    print("\n📝 Agregando productos de muestra...")
    
    # Crear engine
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # Verificar si ya hay productos
        existing_products = db.query(Product).count()
        if existing_products > 0:
            print(f"⚠️ Ya existen {existing_products} productos. No se agregarán productos de muestra.")
            return
        
        # Verificar si hay categorías
        categories = db.query(Category).all()
        if not categories:
            print("⚠️ No hay categorías. Creando categorías por defecto...")
            default_categories = [
                Category(name="Bebidas", description="Bebidas y refrescos"),
                Category(name="Platos Principales", description="Platos principales del menú"),
                Category(name="Entradas", description="Entradas y aperitivos"),
                Category(name="Postres", description="Postres y dulces"),
                Category(name="Ingredientes", description="Ingredientes para cocina"),
                Category(name="Otros", description="Otros productos")
            ]
            for category in default_categories:
                db.add(category)
            db.commit()
            categories = db.query(Category).all()
        
        # Productos de muestra
        sample_products = [
            {
                "name": "Hamburguesa Clásica",
                "price": 12.50,
                "cost_price": 8.00,
                "stock": 50,
                "min_stock": 10,
                "max_stock": 100,
                "category_id": categories[1].id if len(categories) > 1 else categories[0].id,  # Platos Principales
                "description": "Hamburguesa con carne, lechuga, tomate y queso"
            },
            {
                "name": "Coca Cola",
                "price": 2.50,
                "cost_price": 1.50,
                "stock": 100,
                "min_stock": 20,
                "max_stock": 200,
                "category_id": categories[0].id if categories else None,  # Bebidas
                "description": "Refresco Coca Cola 350ml"
            },
            {
                "name": "Papas Fritas",
                "price": 4.00,
                "cost_price": 2.00,
                "stock": 75,
                "min_stock": 15,
                "max_stock": 150,
                "category_id": categories[2].id if len(categories) > 2 else categories[0].id,  # Entradas
                "description": "Papas fritas crujientes"
            },
            {
                "name": "Tiramisú",
                "price": 6.50,
                "cost_price": 3.50,
                "stock": 25,
                "min_stock": 5,
                "max_stock": 50,
                "category_id": categories[3].id if len(categories) > 3 else categories[0].id,  # Postres
                "description": "Postre italiano con café y mascarpone"
            },
            {
                "name": "Carne de Res",
                "price": 15.00,
                "cost_price": 10.00,
                "stock": 30,
                "min_stock": 5,
                "max_stock": 60,
                "category_id": categories[4].id if len(categories) > 4 else categories[0].id,  # Ingredientes
                "description": "Carne de res fresca para hamburguesas"
            }
        ]
        
        # Generar códigos únicos y agregar productos
        import time
        import uuid
        
        for i, product_data in enumerate(sample_products):
            # Generar código único
            timestamp = int(time.time() * 1000) % 1000000
            random_part = uuid.uuid4().hex[:3].upper()
            code = f"PROD{timestamp:06d}{random_part}"
            
            # Crear producto
            product = Product(
                code=code,
                **product_data
            )
            db.add(product)
            print(f"   ✅ Agregado: {product.name} (Código: {code})")
        
        db.commit()
        print(f"🎉 Se agregaron {len(sample_products)} productos de muestra")

if __name__ == "__main__":
    check_database()
    add_sample_products()
    print("\n✅ Verificación completada")
