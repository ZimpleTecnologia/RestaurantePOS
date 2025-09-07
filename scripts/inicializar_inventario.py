#!/usr/bin/env python3
"""
Script para inicializar productos con stock para probar el módulo de inventario
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.product import Product, Category, SubCategory
from app.models.user import User
from app.models.inventory import InventoryMovement
from app.auth.security import get_password_hash

def inicializar_inventario():
    """Inicializar productos con stock para pruebas"""
    db = SessionLocal()
    
    try:
        print("🚀 Inicializando inventario para pruebas...")
        
        # Verificar si ya existen productos con stock
        existing_products = db.query(Product).filter(Product.stock > 0).count()
        if existing_products > 0:
            print(f"⚠️  Ya existen {existing_products} productos con stock")
            print("¿Deseas continuar y agregar más stock? (s/n): ", end="")
            response = input().lower()
            if response != 's':
                print("Operación cancelada")
                return
        
        # Obtener o crear categorías
        bebidas_cat = db.query(Category).filter(Category.name == "Bebidas").first()
        if not bebidas_cat:
            bebidas_cat = Category(name="Bebidas", description="Bebidas y refrescos")
            db.add(bebidas_cat)
            db.commit()
            db.refresh(bebidas_cat)
        
        comidas_cat = db.query(Category).filter(Category.name == "Comidas").first()
        if not comidas_cat:
            comidas_cat = Category(name="Comidas", description="Platos principales")
            db.add(comidas_cat)
            db.commit()
            db.refresh(comidas_cat)
        
        # Obtener o crear subcategorías
        refrescos_sub = db.query(SubCategory).filter(SubCategory.name == "Refrescos").first()
        if not refrescos_sub:
            refrescos_sub = SubCategory(name="Refrescos", category_id=bebidas_cat.id)
            db.add(refrescos_sub)
            db.commit()
            db.refresh(refrescos_sub)
        
        # Productos de ejemplo con stock
        productos_ejemplo = [
            {
                "name": "Coca Cola 350ml",
                "description": "Refresco Coca Cola en lata de 350ml",
                "price": 2.50,
                "stock": 50,
                "min_stock": 10,
                "category_id": bebidas_cat.id,
                "subcategory_id": refrescos_sub.id,
                "code": "COCA350"
            },
            {
                "name": "Pepsi 500ml",
                "description": "Refresco Pepsi en botella de 500ml",
                "price": 3.00,
                "stock": 30,
                "min_stock": 8,
                "category_id": bebidas_cat.id,
                "subcategory_id": refrescos_sub.id,
                "code": "PEPSI500"
            },
            {
                "name": "Agua Mineral 500ml",
                "description": "Agua mineral natural",
                "price": 1.50,
                "stock": 100,
                "min_stock": 20,
                "category_id": bebidas_cat.id,
                "subcategory_id": None,
                "code": "AGUA500"
            },
            {
                "name": "Hamburguesa Clásica",
                "description": "Hamburguesa con carne, lechuga, tomate y queso",
                "price": 8.50,
                "stock": 25,
                "min_stock": 5,
                "category_id": comidas_cat.id,
                "subcategory_id": None,
                "code": "HAMB-CLAS"
            },
            {
                "name": "Pizza Margherita",
                "description": "Pizza con tomate, mozzarella y albahaca",
                "price": 12.00,
                "stock": 15,
                "min_stock": 3,
                "category_id": comidas_cat.id,
                "subcategory_id": None,
                "code": "PIZZA-MARG"
            },
            {
                "name": "Ensalada César",
                "description": "Ensalada con lechuga, crutones, parmesano y aderezo César",
                "price": 6.50,
                "stock": 20,
                "min_stock": 5,
                "category_id": comidas_cat.id,
                "subcategory_id": None,
                "code": "ENS-CESAR"
            },
            {
                "name": "Papas Fritas",
                "description": "Porción de papas fritas crujientes",
                "price": 4.00,
                "stock": 40,
                "min_stock": 10,
                "category_id": comidas_cat.id,
                "subcategory_id": None,
                "code": "PAPAS-FRIT"
            },
            {
                "name": "Cerveza Nacional",
                "description": "Cerveza nacional 330ml",
                "price": 4.50,
                "stock": 60,
                "min_stock": 15,
                "category_id": bebidas_cat.id,
                "subcategory_id": None,
                "code": "CERVEZA330"
            }
        ]
        
        productos_creados = []
        
        for producto_data in productos_ejemplo:
            # Verificar si el producto ya existe
            existing_product = db.query(Product).filter(Product.name == producto_data["name"]).first()
            
            if existing_product:
                # Actualizar stock si existe
                existing_product.stock = producto_data["stock"]
                existing_product.min_stock = producto_data["min_stock"]
                print(f"✅ Actualizado: {existing_product.name} - Stock: {existing_product.stock}")
                productos_creados.append(existing_product)
            else:
                # Crear nuevo producto
                producto = Product(
                    name=producto_data["name"],
                    description=producto_data["description"],
                    price=producto_data["price"],
                    stock=producto_data["stock"],
                    min_stock=producto_data["min_stock"],
                    category_id=producto_data["category_id"],
                    subcategory_id=producto_data["subcategory_id"],
                    code=producto_data["code"],
                    product_type="producto"
                )
                db.add(producto)
                productos_creados.append(producto)
                print(f"✅ Creado: {producto.name} - Stock: {producto.stock}")
        
        db.commit()
        
        # Crear movimientos de inventario iniciales
        print("\n📝 Creando movimientos de inventario iniciales...")
        
        # Obtener usuario admin para los movimientos
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("⚠️  Usuario admin no encontrado, creando...")
            admin_user = User(
                username="admin",
                email="admin@restaurante.com",
                full_name="Administrador del Sistema",
                hashed_password=get_password_hash("admin123"),
                role="ADMIN",
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        
        for producto in productos_creados:
            # Crear movimiento inicial
            movimiento = InventoryMovement(
                product_id=producto.id,
                adjustment_type="add",
                quantity=producto.stock,
                previous_stock=0,
                new_stock=producto.stock,
                reason="inventario",
                notes="Inicialización de inventario para pruebas",
                user_id=admin_user.id
            )
            db.add(movimiento)
            print(f"📊 Movimiento creado: {producto.name} - {producto.stock} unidades")
        
        db.commit()
        
        print(f"\n🎉 Inventario inicializado exitosamente!")
        print(f"📦 Productos creados/actualizados: {len(productos_creados)}")
        print(f"📊 Movimientos de inventario: {len(productos_creados)}")
        
        # Mostrar resumen
        total_stock = sum(p.stock for p in productos_creados)
        total_value = sum(p.stock * p.price for p in productos_creados)
        
        print(f"\n📈 Resumen del inventario:")
        print(f"   Total de productos: {len(productos_creados)}")
        print(f"   Total de unidades: {total_stock}")
        print(f"   Valor total: ${total_value:.2f}")
        
        # Mostrar productos con stock bajo
        productos_bajo_stock = [p for p in productos_creados if p.stock <= p.min_stock]
        if productos_bajo_stock:
            print(f"\n⚠️  Productos con stock bajo:")
            for p in productos_bajo_stock:
                print(f"   - {p.name}: {p.stock}/{p.min_stock}")
        
        print(f"\n🚀 Para probar el módulo:")
        print(f"   1. Inicia la aplicación: python -m uvicorn app.main:app --reload")
        print(f"   2. Ve a: http://localhost:8000/inventory")
        print(f"   3. Inicia sesión con: admin / admin123")
        
    except Exception as e:
        print(f"❌ Error inicializando inventario: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    inicializar_inventario()
