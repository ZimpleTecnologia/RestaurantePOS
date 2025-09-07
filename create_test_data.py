#!/usr/bin/env python3
"""
Script para crear datos de prueba para meseros y cocina
"""
import sys
import os

# Agregar path de la aplicación
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import SessionLocal, create_tables
    from app.models.user import User, UserRole
    from app.models.location import Table, TableStatus
    from app.models.product import Product, ProductType, Category, Subcategory
    from app.models.order import Order, OrderItem
    from app.auth.security import get_password_hash
    from datetime import datetime
    
    def create_test_data():
        print("🔧 Creando datos de prueba...")
        
        # Crear tablas
        create_tables()
        print("✅ Tablas verificadas")
        
        db = SessionLocal()
        
        try:
            # Crear usuarios de prueba
            print("👥 Creando usuarios de prueba...")
            
            # Mesero 1
            mesero1 = db.query(User).filter(User.username == 'mesero1').first()
            if not mesero1:
                mesero1 = User(
                    username='mesero1',
                    email='mesero1@restaurante.com',
                    full_name='Juan Pérez',
                    hashed_password=get_password_hash('mesero123'),
                    role=UserRole.MESERO,
                    is_active=True,
                    is_verified=True
                )
                db.add(mesero1)
                print("✅ Mesero 1 creado")
            
            # Mesero 2
            mesero2 = db.query(User).filter(User.username == 'mesero2').first()
            if not mesero2:
                mesero2 = User(
                    username='mesero2',
                    email='mesero2@restaurante.com',
                    full_name='María García',
                    hashed_password=get_password_hash('mesero123'),
                    role=UserRole.MESERO,
                    is_active=True,
                    is_verified=True
                )
                db.add(mesero2)
                print("✅ Mesero 2 creado")
            
            # Cocinero 1
            cocinero1 = db.query(User).filter(User.username == 'cocinero1').first()
            if not cocinero1:
                cocinero1 = User(
                    username='cocinero1',
                    email='cocinero1@restaurante.com',
                    full_name='Carlos López',
                    hashed_password=get_password_hash('cocina123'),
                    role=UserRole.COCINA,
                    is_active=True,
                    is_verified=True
                )
                db.add(cocinero1)
                print("✅ Cocinero 1 creado")
            
            # Cocinero 2
            cocinero2 = db.query(User).filter(User.username == 'cocinero2').first()
            if not cocinero2:
                cocinero2 = User(
                    username='cocinero2',
                    email='cocinero2@restaurante.com',
                    full_name='Ana Rodríguez',
                    hashed_password=get_password_hash('cocina123'),
                    role=UserRole.COCINA,
                    is_active=True,
                    is_verified=True
                )
                db.add(cocinero2)
                print("✅ Cocinero 2 creado")
            
            db.commit()
            
            # Crear mesas
            print("🪑 Creando mesas...")
            tables_data = [
                {"table_number": 1, "capacity": 4, "status": TableStatus.FREE},
                {"table_number": 2, "capacity": 6, "status": TableStatus.FREE},
                {"table_number": 3, "capacity": 4, "status": TableStatus.FREE},
                {"table_number": 4, "capacity": 8, "status": TableStatus.FREE},
                {"table_number": 5, "capacity": 2, "status": TableStatus.FREE},
                {"table_number": 6, "capacity": 4, "status": TableStatus.FREE},
                {"table_number": 7, "capacity": 6, "status": TableStatus.FREE},
                {"table_number": 8, "capacity": 4, "status": TableStatus.FREE},
            ]
            
            for table_data in tables_data:
                existing_table = db.query(Table).filter(Table.table_number == table_data["table_number"]).first()
                if not existing_table:
                    table = Table(**table_data)
                    db.add(table)
                    print(f"✅ Mesa {table_data['table_number']} creada")
            
            db.commit()
            
            # Crear categorías y subcategorías
            print("📂 Creando categorías...")
            
            # Categoría: Platos Principales
            categoria_principales = db.query(Category).filter(Category.name == "Platos Principales").first()
            if not categoria_principales:
                categoria_principales = Category(name="Platos Principales", description="Platos principales del menú")
                db.add(categoria_principales)
                db.commit()
                db.refresh(categoria_principales)
                print("✅ Categoría 'Platos Principales' creada")
            
            # Subcategorías
            subcategorias = [
                {"name": "Carnes", "category_id": categoria_principales.id},
                {"name": "Pescados", "category_id": categoria_principales.id},
                {"name": "Pastas", "category_id": categoria_principales.id},
            ]
            
            for subcat_data in subcategorias:
                existing_subcat = db.query(Subcategory).filter(
                    Subcategory.name == subcat_data["name"],
                    Subcategory.category_id == subcat_data["category_id"]
                ).first()
                if not existing_subcat:
                    subcat = Subcategory(**subcat_data)
                    db.add(subcat)
                    print(f"✅ Subcategoría '{subcat_data['name']}' creada")
            
            db.commit()
            
            # Crear productos
            print("🍽️ Creando productos...")
            productos_data = [
                {
                    "name": "Bistec a la Plancha",
                    "description": "Bistec de res a la plancha con guarnición",
                    "price": 15.99,
                    "cost": 8.50,
                    "category_id": categoria_principales.id,
                    "product_type": ProductType.PLATO,
                    "is_active": True
                },
                {
                    "name": "Pescado Frito",
                    "description": "Pescado fresco frito con papas fritas",
                    "price": 18.99,
                    "cost": 10.00,
                    "category_id": categoria_principales.id,
                    "product_type": ProductType.PLATO,
                    "is_active": True
                },
                {
                    "name": "Espagueti Carbonara",
                    "description": "Espagueti con salsa carbonara y queso parmesano",
                    "price": 12.99,
                    "cost": 6.50,
                    "category_id": categoria_principales.id,
                    "product_type": ProductType.PLATO,
                    "is_active": True
                },
                {
                    "name": "Ensalada César",
                    "description": "Ensalada con lechuga, crutones y aderezo César",
                    "price": 8.99,
                    "cost": 4.00,
                    "category_id": categoria_principales.id,
                    "product_type": ProductType.PLATO,
                    "is_active": True
                },
                {
                    "name": "Sopa del Día",
                    "description": "Sopa casera del día",
                    "price": 6.99,
                    "cost": 3.00,
                    "category_id": categoria_principales.id,
                    "product_type": ProductType.PLATO,
                    "is_active": True
                }
            ]
            
            for producto_data in productos_data:
                existing_product = db.query(Product).filter(Product.name == producto_data["name"]).first()
                if not existing_product:
                    producto = Product(**producto_data)
                    db.add(producto)
                    print(f"✅ Producto '{producto_data['name']}' creado")
            
            db.commit()
            
            # Crear algunas órdenes de prueba
            print("📋 Creando órdenes de prueba...")
            
            # Obtener mesas y productos
            mesa1 = db.query(Table).filter(Table.table_number == 1).first()
            mesa2 = db.query(Table).filter(Table.table_number == 2).first()
            bistec = db.query(Product).filter(Product.name == "Bistec a la Plancha").first()
            pescado = db.query(Product).filter(Product.name == "Pescado Frito").first()
            ensalada = db.query(Product).filter(Product.name == "Ensalada César").first()
            
            if mesa1 and mesa2 and bistec and pescado and ensalada:
                # Orden 1 - Pendiente
                order1 = Order(
                    order_number="ORD-20250824-0001",
                    table_id=mesa1.id,
                    waiter_id=mesero1.id,
                    people_count=4,
                    status="pendiente",
                    priority="normal",
                    notes="Sin cebolla en el bistec"
                )
                db.add(order1)
                db.commit()
                db.refresh(order1)
                
                # Items de la orden 1
                item1_1 = OrderItem(
                    order_id=order1.id,
                    product_id=bistec.id,
                    quantity=2,
                    unit_price=15.99,
                    subtotal=31.98,
                    special_instructions="Sin cebolla"
                )
                item1_2 = OrderItem(
                    order_id=order1.id,
                    product_id=ensalada.id,
                    quantity=1,
                    unit_price=8.99,
                    subtotal=8.99
                )
                db.add_all([item1_1, item1_2])
                print("✅ Orden 1 creada (pendiente)")
                
                # Orden 2 - En preparación
                order2 = Order(
                    order_number="ORD-20250824-0002",
                    table_id=mesa2.id,
                    waiter_id=mesero2.id,
                    people_count=2,
                    status="en_preparacion",
                    priority="alta",
                    kitchen_start_time=datetime.now()
                )
                db.add(order2)
                db.commit()
                db.refresh(order2)
                
                # Items de la orden 2
                item2_1 = OrderItem(
                    order_id=order2.id,
                    product_id=pescado.id,
                    quantity=1,
                    unit_price=18.99,
                    subtotal=18.99,
                    status="en_preparacion",
                    kitchen_start_time=datetime.now()
                )
                item2_2 = OrderItem(
                    order_id=order2.id,
                    product_id=ensalada.id,
                    quantity=1,
                    unit_price=8.99,
                    subtotal=8.99,
                    status="en_preparacion",
                    kitchen_start_time=datetime.now()
                )
                db.add_all([item2_1, item2_2])
                print("✅ Orden 2 creada (en preparación)")
                
                # Actualizar estado de las mesas
                mesa1.status = TableStatus.OCCUPIED
                mesa2.status = TableStatus.OCCUPIED
                
                db.commit()
                print("✅ Estados de mesas actualizados")
            
            print("🎉 Datos de prueba creados exitosamente!")
            print("\n📋 Credenciales de prueba:")
            print("   Mesero 1: mesero1 / mesero123")
            print("   Mesero 2: mesero2 / mesero123")
            print("   Cocinero 1: cocinero1 / cocina123")
            print("   Cocinero 2: cocinero2 / cocina123")
            print("   Admin: admin / admin123")
            
            return True
                
        except Exception as e:
            db.rollback()
            print(f"❌ Error: {e}")
            return False
        finally:
            db.close()
    
    if __name__ == "__main__":
        success = create_test_data()
        sys.exit(0 if success else 1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

