#!/usr/bin/env python3
"""
Script para inicializar productos de ejemplo del restaurante usando SQL directo
"""
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text

def inicializar_productos_sql():
    """Inicializar productos de ejemplo usando SQL directo"""
    db = SessionLocal()
    
    try:
        print("🍽️ Inicializando productos del restaurante...")
        
        # Verificar si ya existen productos
        result = db.execute(text("SELECT COUNT(*) FROM products"))
        existing_products = result.scalar()
        if existing_products > 0:
            print(f"✅ Ya existen {existing_products} productos en la base de datos")
            return
        
        # Crear categorías
        categorias = [
            ("Bebidas", "Bebidas y refrescos"),
            ("Platos Principales", "Platos principales del menú"),
            ("Aperitivos", "Entradas y aperitivos"),
            ("Postres", "Postres y dulces")
        ]
        
        categorias_creadas = {}
        for nombre, descripcion in categorias:
            result = db.execute(text("""
                INSERT INTO categories (name, description, is_active) 
                VALUES (:name, :description, true) 
                RETURNING id
            """), {"name": nombre, "description": descripcion})
            categoria_id = result.scalar()
            categorias_creadas[nombre] = categoria_id
        
        # Crear subcategorías
        subcategorias = [
            ("Refrescos", categorias_creadas["Bebidas"]),
            ("Aguas", categorias_creadas["Bebidas"]),
            ("Jugos", categorias_creadas["Bebidas"]),
            ("Cervezas", categorias_creadas["Bebidas"]),
            ("Hamburguesas", categorias_creadas["Platos Principales"]),
            ("Pizzas", categorias_creadas["Platos Principales"]),
            ("Pastas", categorias_creadas["Platos Principales"]),
            ("Ensaladas", categorias_creadas["Platos Principales"]),
            ("Carnes", categorias_creadas["Platos Principales"]),
            ("Frituras", categorias_creadas["Aperitivos"]),
            ("Helados", categorias_creadas["Postres"]),
            ("Pasteles", categorias_creadas["Postres"])
        ]
        
        subcategorias_creadas = {}
        for nombre, categoria_id in subcategorias:
            result = db.execute(text("""
                INSERT INTO subcategories (name, category_id, is_active) 
                VALUES (:name, :category_id, true) 
                RETURNING id
            """), {"name": nombre, "category_id": categoria_id})
            subcategoria_id = result.scalar()
            subcategorias_creadas[nombre] = subcategoria_id
        
        # Productos de ejemplo
        productos = [
            # Bebidas
            ("BEV001", "Coca Cola", "Refresco Coca Cola 350ml", 2.50, 1.20, 100, categorias_creadas["Bebidas"], subcategorias_creadas["Refrescos"]),
            ("BEV002", "Agua Mineral", "Agua mineral sin gas 500ml", 1.50, 0.80, 50, categorias_creadas["Bebidas"], subcategorias_creadas["Aguas"]),
            ("BEV003", "Jugo de Naranja", "Jugo de naranja natural 300ml", 3.00, 1.50, 30, categorias_creadas["Bebidas"], subcategorias_creadas["Jugos"]),
            ("BEV004", "Cerveza Nacional", "Cerveza nacional 330ml", 4.00, 2.00, 80, categorias_creadas["Bebidas"], subcategorias_creadas["Cervezas"]),
            
            # Platos Principales
            ("MAIN001", "Hamburguesa Clásica", "Hamburguesa con carne, lechuga, tomate y queso", 8.50, 4.00, 20, categorias_creadas["Platos Principales"], subcategorias_creadas["Hamburguesas"]),
            ("MAIN002", "Pizza Margherita", "Pizza con salsa de tomate, mozzarella y albahaca", 12.00, 6.00, 15, categorias_creadas["Platos Principales"], subcategorias_creadas["Pizzas"]),
            ("MAIN003", "Pasta Carbonara", "Pasta con salsa carbonara, panceta y parmesano", 10.50, 5.00, 12, categorias_creadas["Platos Principales"], subcategorias_creadas["Pastas"]),
            ("MAIN004", "Ensalada César", "Ensalada con lechuga, crutones, parmesano y aderezo César", 7.00, 3.50, 8, categorias_creadas["Platos Principales"], subcategorias_creadas["Ensaladas"]),
            ("MAIN005", "Pollo a la Plancha", "Pechuga de pollo a la plancha con guarnición", 11.00, 5.50, 10, categorias_creadas["Platos Principales"], subcategorias_creadas["Carnes"]),
            
            # Aperitivos
            ("APP001", "Papas Fritas", "Porción de papas fritas crujientes", 4.50, 2.00, 25, categorias_creadas["Aperitivos"], subcategorias_creadas["Frituras"]),
            ("APP002", "Nuggets de Pollo", "6 nuggets de pollo con salsa", 5.50, 2.50, 20, categorias_creadas["Aperitivos"], subcategorias_creadas["Frituras"]),
            ("APP003", "Aros de Cebolla", "Aros de cebolla empanizados", 4.00, 1.80, 15, categorias_creadas["Aperitivos"], subcategorias_creadas["Frituras"]),
            
            # Postres
            ("DES001", "Tiramisú", "Postre italiano con café y mascarpone", 6.50, 3.00, 10, categorias_creadas["Postres"], subcategorias_creadas["Pasteles"]),
            ("DES002", "Helado de Vainilla", "Helado de vainilla con toppings", 4.00, 1.50, 15, categorias_creadas["Postres"], subcategorias_creadas["Helados"]),
            ("DES003", "Brownie", "Brownie de chocolate con nueces", 5.00, 2.20, 12, categorias_creadas["Postres"], subcategorias_creadas["Pasteles"])
        ]
        
        # Crear productos
        productos_creados = []
        for code, name, description, price, cost_price, stock, category_id, subcategory_id in productos:
            result = db.execute(text("""
                INSERT INTO products (code, name, description, price, cost_price, stock, category_id, subcategory_id, product_type, is_active) 
                VALUES (:code, :name, :description, :price, :cost_price, :stock, :category_id, :subcategory_id, 'producto', true) 
                RETURNING id, name
            """), {
                "code": code, "name": name, "description": description, 
                "price": price, "cost_price": cost_price, "stock": stock,
                "category_id": category_id, "subcategory_id": subcategory_id
            })
            producto_id, producto_name = result.fetchone()
            productos_creados.append((producto_id, producto_name, price))
        
        db.commit()
        
        print(f"✅ Se crearon {len(productos_creados)} productos exitosamente:")
        print()
        
        # Mostrar productos por categoría
        for categoria_nombre, categoria_id in categorias_creadas.items():
            print(f"📂 {categoria_nombre.upper()}:")
            productos_cat = [p for p in productos_creados if p[0] in [pid for pid, _, _ in productos_creados if pid]]
            for _, nombre, precio in productos_cat:
                print(f"  🍽️ {nombre} - ${precio}")
            print()
        
        print("🎉 Inicialización de productos completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    inicializar_productos_sql()
