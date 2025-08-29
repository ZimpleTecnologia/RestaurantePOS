#!/usr/bin/env python3
"""
Script para inicializar productos de ejemplo del restaurante
"""
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product, Category, SubCategory
from decimal import Decimal

def inicializar_productos():
    """Inicializar productos de ejemplo"""
    db = SessionLocal()
    
    try:
        print("🍽️ Inicializando productos del restaurante...")
        
        # Verificar si ya existen productos
        existing_products = db.query(Product).count()
        if existing_products > 0:
            print(f"✅ Ya existen {existing_products} productos en la base de datos")
            return
        
        # Crear categorías
        categorias = [
            {"name": "Bebidas", "description": "Bebidas y refrescos"},
            {"name": "Platos Principales", "description": "Platos principales del menú"},
            {"name": "Aperitivos", "description": "Entradas y aperitivos"},
            {"name": "Postres", "description": "Postres y dulces"}
        ]
        
        categorias_creadas = {}
        for cat_data in categorias:
            categoria = Category(**cat_data)
            db.add(categoria)
            db.flush()  # Para obtener el ID
            categorias_creadas[cat_data["name"]] = categoria
        
        # Crear subcategorías
        subcategorias = [
            {"name": "Refrescos", "category_id": categorias_creadas["Bebidas"].id},
            {"name": "Aguas", "category_id": categorias_creadas["Bebidas"].id},
            {"name": "Jugos", "category_id": categorias_creadas["Bebidas"].id},
            {"name": "Cervezas", "category_id": categorias_creadas["Bebidas"].id},
            {"name": "Hamburguesas", "category_id": categorias_creadas["Platos Principales"].id},
            {"name": "Pizzas", "category_id": categorias_creadas["Platos Principales"].id},
            {"name": "Pastas", "category_id": categorias_creadas["Platos Principales"].id},
            {"name": "Ensaladas", "category_id": categorias_creadas["Platos Principales"].id},
            {"name": "Carnes", "category_id": categorias_creadas["Platos Principales"].id},
            {"name": "Frituras", "category_id": categorias_creadas["Aperitivos"].id},
            {"name": "Helados", "category_id": categorias_creadas["Postres"].id},
            {"name": "Pasteles", "category_id": categorias_creadas["Postres"].id}
        ]
        
        subcategorias_creadas = {}
        for subcat_data in subcategorias:
            subcategoria = SubCategory(**subcat_data)
            db.add(subcategoria)
            db.flush()  # Para obtener el ID
            subcategorias_creadas[subcat_data["name"]] = subcategoria
        
        # Productos de ejemplo
        productos = [
            # Bebidas
            {
                "code": "BEV001",
                "name": "Coca Cola",
                "description": "Refresco Coca Cola 350ml",
                "price": 2.50,
                "cost_price": 1.20,
                "stock": 100,
                "category_id": categorias_creadas["Bebidas"].id,
                "subcategory_id": subcategorias_creadas["Refrescos"].id,
                "is_active": True
            },
            {
                "code": "BEV002",
                "name": "Agua Mineral",
                "description": "Agua mineral sin gas 500ml",
                "price": 1.50,
                "cost_price": 0.80,
                "stock": 50,
                "category_id": categorias_creadas["Bebidas"].id,
                "subcategory_id": subcategorias_creadas["Aguas"].id,
                "is_active": True
            },
            {
                "code": "BEV003",
                "name": "Jugo de Naranja",
                "description": "Jugo de naranja natural 300ml",
                "price": 3.00,
                "cost_price": 1.50,
                "stock": 30,
                "category_id": categorias_creadas["Bebidas"].id,
                "subcategory_id": subcategorias_creadas["Jugos"].id,
                "is_active": True
            },
            {
                "code": "BEV004",
                "name": "Cerveza Nacional",
                "description": "Cerveza nacional 330ml",
                "price": 4.00,
                "cost_price": 2.00,
                "stock": 80,
                "category_id": categorias_creadas["Bebidas"].id,
                "subcategory_id": subcategorias_creadas["Cervezas"].id,
                "is_active": True
            },
            
            # Platos Principales
            {
                "code": "MAIN001",
                "name": "Hamburguesa Clásica",
                "description": "Hamburguesa con carne, lechuga, tomate y queso",
                "price": 8.50,
                "cost_price": 4.00,
                "stock": 20,
                "category_id": categorias_creadas["Platos Principales"].id,
                "subcategory_id": subcategorias_creadas["Hamburguesas"].id,
                "is_active": True
            },
            {
                "code": "MAIN002",
                "name": "Pizza Margherita",
                "description": "Pizza con salsa de tomate, mozzarella y albahaca",
                "price": 12.00,
                "cost_price": 6.00,
                "stock": 15,
                "category_id": categorias_creadas["Platos Principales"].id,
                "subcategory_id": subcategorias_creadas["Pizzas"].id,
                "is_active": True
            },
            {
                "code": "MAIN003",
                "name": "Pasta Carbonara",
                "description": "Pasta con salsa carbonara, panceta y parmesano",
                "price": 10.50,
                "cost_price": 5.00,
                "stock": 12,
                "category_id": categorias_creadas["Platos Principales"].id,
                "subcategory_id": subcategorias_creadas["Pastas"].id,
                "is_active": True
            },
            {
                "code": "MAIN004",
                "name": "Ensalada César",
                "description": "Ensalada con lechuga, crutones, parmesano y aderezo César",
                "price": 7.00,
                "cost_price": 3.50,
                "stock": 8,
                "category_id": categorias_creadas["Platos Principales"].id,
                "subcategory_id": subcategorias_creadas["Ensaladas"].id,
                "is_active": True
            },
            {
                "code": "MAIN005",
                "name": "Pollo a la Plancha",
                "description": "Pechuga de pollo a la plancha con guarnición",
                "price": 11.00,
                "cost_price": 5.50,
                "stock": 10,
                "category_id": categorias_creadas["Platos Principales"].id,
                "subcategory_id": subcategorias_creadas["Carnes"].id,
                "is_active": True
            },
            
            # Aperitivos
            {
                "code": "APP001",
                "name": "Papas Fritas",
                "description": "Porción de papas fritas crujientes",
                "price": 4.50,
                "cost_price": 2.00,
                "stock": 25,
                "category_id": categorias_creadas["Aperitivos"].id,
                "subcategory_id": subcategorias_creadas["Frituras"].id,
                "is_active": True
            },
            {
                "code": "APP002",
                "name": "Nuggets de Pollo",
                "description": "6 nuggets de pollo con salsa",
                "price": 5.50,
                "cost_price": 2.50,
                "stock": 20,
                "category_id": categorias_creadas["Aperitivos"].id,
                "subcategory_id": subcategorias_creadas["Frituras"].id,
                "is_active": True
            },
            {
                "code": "APP003",
                "name": "Aros de Cebolla",
                "description": "Aros de cebolla empanizados",
                "price": 4.00,
                "cost_price": 1.80,
                "stock": 15,
                "category_id": categorias_creadas["Aperitivos"].id,
                "subcategory_id": subcategorias_creadas["Frituras"].id,
                "is_active": True
            },
            
            # Postres
            {
                "code": "DES001",
                "name": "Tiramisú",
                "description": "Postre italiano con café y mascarpone",
                "price": 6.50,
                "cost_price": 3.00,
                "stock": 10,
                "category_id": categorias_creadas["Postres"].id,
                "subcategory_id": subcategorias_creadas["Pasteles"].id,
                "is_active": True
            },
            {
                "code": "DES002",
                "name": "Helado de Vainilla",
                "description": "Helado de vainilla con toppings",
                "price": 4.00,
                "cost_price": 1.50,
                "stock": 15,
                "category_id": categorias_creadas["Postres"].id,
                "subcategory_id": subcategorias_creadas["Helados"].id,
                "is_active": True
            },
            {
                "code": "DES003",
                "name": "Brownie",
                "description": "Brownie de chocolate con nueces",
                "price": 5.00,
                "cost_price": 2.20,
                "stock": 12,
                "category_id": categorias_creadas["Postres"].id,
                "subcategory_id": subcategorias_creadas["Pasteles"].id,
                "is_active": True
            }
        ]
        
        # Crear productos uno por uno
        productos_creados = []
        for producto_data in productos:
            producto = Product(**producto_data)
            db.add(producto)
            db.flush()  # Para obtener el ID
            productos_creados.append(producto)
        
        db.commit()
        
        print(f"✅ Se crearon {len(productos_creados)} productos exitosamente:")
        print()
        
        # Mostrar productos por categoría
        for categoria in categorias_creadas.values():
            print(f"📂 {categoria.name.upper()}:")
            productos_cat = [p for p in productos_creados if p.category_id == categoria.id]
            for producto in productos_cat:
                print(f"  🍽️ {producto.name} - ${producto.price}")
            print()
        
        print("🎉 Inicialización de productos completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    inicializar_productos()
