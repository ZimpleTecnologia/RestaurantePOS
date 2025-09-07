#!/usr/bin/env python3
"""
Script para crear datos de prueba mejorados para el sistema POS
Genera datos realistas para un restaurante pequeño
"""
import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar variables de entorno
os.environ["DATABASE_URL"] = "postgresql://sistema_pos_user:sistema_pos_password@localhost:5432/sistema_pos"
os.environ["SECRET_KEY"] = "tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DEBUG"] = "True"

# Agregar path de la aplicación
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, create_tables
from app.models.user import User, UserRole
from app.models.product import Product, ProductCategory
from app.models.location import Table, TableStatus
from app.models.supplier import Supplier
from app.models.customer import Customer
from app.models.order import Order, OrderItem, OrderStatus, OrderType
from app.models.inventory import InventoryLocation, InventoryLot, InventoryMovement, MovementType, MovementReason
from app.auth.security import get_password_hash


def create_test_users(db):
    """Crear usuarios de prueba"""
    print("👥 Creando usuarios de prueba...")
    
    users_data = [
        {
            "username": "admin",
            "email": "admin@restaurante.com",
            "full_name": "Administrador del Sistema",
            "password": "admin123",
            "role": UserRole.ADMIN
        },
        {
            "username": "maria",
            "email": "maria@restaurante.com",
            "full_name": "María González",
            "password": "maria123",
            "role": UserRole.MESERO
        },
        {
            "username": "carlos",
            "email": "carlos@restaurante.com",
            "full_name": "Carlos Rodríguez",
            "password": "carlos123",
            "role": UserRole.MESERO
        },
        {
            "username": "chef",
            "email": "chef@restaurante.com",
            "full_name": "Chef Juan Pérez",
            "password": "chef123",
            "role": UserRole.COCINA
        },
        {
            "username": "caja",
            "email": "caja@restaurante.com",
            "full_name": "Ana López",
            "password": "caja123",
            "role": UserRole.CAJA
        },
        {
            "username": "almacen",
            "email": "almacen@restaurante.com",
            "full_name": "Roberto Silva",
            "password": "almacen123",
            "role": UserRole.ALMACEN
        }
    ]
    
    for user_data in users_data:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            hashed_password = get_password_hash(user_data["password"])
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hashed_password,
                role=user_data["role"],
                is_active=True,
                is_verified=True
            )
            db.add(user)
            print(f"   ✅ Usuario creado: {user_data['username']} ({user_data['role']})")
    
    db.commit()


def create_test_suppliers(db):
    """Crear proveedores de prueba"""
    print("🏪 Creando proveedores de prueba...")
    
    suppliers_data = [
        {
            "name": "Distribuidora Central",
            "contact_person": "Luis Mendoza",
            "phone": "300-123-4567",
            "email": "ventas@distribuidoracentral.com",
            "address": "Calle 45 #12-34, Bogotá",
            "tax_id": "900123456-7"
        },
        {
            "name": "Carnes Premium",
            "contact_person": "Carmen Vargas",
            "phone": "310-987-6543",
            "email": "carmen@carnespremium.com",
            "address": "Carrera 78 #23-45, Medellín",
            "tax_id": "900987654-3"
        },
        {
            "name": "Verduras Frescas",
            "contact_person": "Pedro Ramírez",
            "phone": "315-456-7890",
            "email": "pedro@verdurasfrescas.com",
            "address": "Calle 12 #67-89, Cali",
            "tax_id": "900456789-0"
        },
        {
            "name": "Bebidas Nacionales",
            "contact_person": "Sofia Torres",
            "phone": "320-111-2222",
            "email": "sofia@bebidasnacionales.com",
            "address": "Carrera 15 #90-12, Barranquilla",
            "tax_id": "900111222-2"
        }
    ]
    
    suppliers = []
    for supplier_data in suppliers_data:
        existing_supplier = db.query(Supplier).filter(Supplier.name == supplier_data["name"]).first()
        if not existing_supplier:
            supplier = Supplier(**supplier_data)
            db.add(supplier)
            suppliers.append(supplier)
            print(f"   ✅ Proveedor creado: {supplier_data['name']}")
    
    db.commit()
    return suppliers


def create_test_products(db, suppliers):
    """Crear productos de prueba"""
    print("🍽️ Creando productos de prueba...")
    
    products_data = [
        # Entradas
        {
            "name": "Ensalada César",
            "description": "Lechuga romana, crutones, parmesano y aderezo César",
            "price": Decimal("12000"),
            "cost_price": Decimal("8000"),
            "category": ProductCategory.ENTRADA,
            "track_stock": True,
            "stock_quantity": 50,
            "min_stock_level": 10,
            "max_stock_level": 100,
            "reorder_point": 15,
            "unit": "porción",
            "barcode": "1234567890123",
            "sku": "ENT-001"
        },
        {
            "name": "Sopa del Día",
            "description": "Sopa casera preparada diariamente",
            "price": Decimal("8000"),
            "cost_price": Decimal("4000"),
            "category": ProductCategory.ENTRADA,
            "track_stock": True,
            "stock_quantity": 30,
            "min_stock_level": 5,
            "max_stock_level": 50,
            "reorder_point": 8,
            "unit": "porción",
            "barcode": "1234567890124",
            "sku": "ENT-002"
        },
        
        # Platos Principales
        {
            "name": "Bandeja Paisa",
            "description": "Arroz, frijoles, carne, chicharrón, huevo, plátano y aguacate",
            "price": Decimal("25000"),
            "cost_price": Decimal("15000"),
            "category": ProductCategory.PLATO_PRINCIPAL,
            "track_stock": True,
            "stock_quantity": 25,
            "min_stock_level": 5,
            "max_stock_level": 40,
            "reorder_point": 8,
            "unit": "plato",
            "barcode": "1234567890125",
            "sku": "PP-001"
        },
        {
            "name": "Pechuga a la Plancha",
            "description": "Pechuga de pollo a la plancha con guarnición",
            "price": Decimal("18000"),
            "cost_price": Decimal("10000"),
            "category": ProductCategory.PLATO_PRINCIPAL,
            "track_stock": True,
            "stock_quantity": 35,
            "min_stock_level": 8,
            "max_stock_level": 50,
            "reorder_point": 12,
            "unit": "plato",
            "barcode": "1234567890126",
            "sku": "PP-002"
        },
        {
            "name": "Pasta Carbonara",
            "description": "Pasta con salsa carbonara, panceta y parmesano",
            "price": Decimal("16000"),
            "cost_price": Decimal("9000"),
            "category": ProductCategory.PLATO_PRINCIPAL,
            "track_stock": True,
            "stock_quantity": 20,
            "min_stock_level": 5,
            "max_stock_level": 30,
            "reorder_point": 8,
            "unit": "plato",
            "barcode": "1234567890127",
            "sku": "PP-003"
        },
        
        # Postres
        {
            "name": "Tiramisú",
            "description": "Postre italiano con café y mascarpone",
            "price": Decimal("8000"),
            "cost_price": Decimal("4000"),
            "category": ProductCategory.POSTRE,
            "track_stock": True,
            "stock_quantity": 15,
            "min_stock_level": 3,
            "max_stock_level": 25,
            "reorder_point": 5,
            "unit": "porción",
            "barcode": "1234567890128",
            "sku": "POST-001"
        },
        {
            "name": "Flan de Caramelo",
            "description": "Flan casero con caramelo",
            "price": Decimal("6000"),
            "cost_price": Decimal("3000"),
            "category": ProductCategory.POSTRE,
            "track_stock": True,
            "stock_quantity": 20,
            "min_stock_level": 5,
            "max_stock_level": 30,
            "reorder_point": 8,
            "unit": "porción",
            "barcode": "1234567890129",
            "sku": "POST-002"
        },
        
        # Bebidas
        {
            "name": "Limonada Natural",
            "description": "Limonada natural con limones frescos",
            "price": Decimal("4000"),
            "cost_price": Decimal("1500"),
            "category": ProductCategory.BEBIDA,
            "track_stock": True,
            "stock_quantity": 40,
            "min_stock_level": 10,
            "max_stock_level": 60,
            "reorder_point": 15,
            "unit": "vaso",
            "barcode": "1234567890130",
            "sku": "BEB-001"
        },
        {
            "name": "Jugo de Naranja",
            "description": "Jugo de naranja natural",
            "price": Decimal("5000"),
            "cost_price": Decimal("2000"),
            "category": ProductCategory.BEBIDA,
            "track_stock": True,
            "stock_quantity": 30,
            "min_stock_level": 8,
            "max_stock_level": 45,
            "reorder_point": 12,
            "unit": "vaso",
            "barcode": "1234567890131",
            "sku": "BEB-002"
        },
        {
            "name": "Coca Cola",
            "description": "Gaseosa Coca Cola 350ml",
            "price": Decimal("3000"),
            "cost_price": Decimal("1200"),
            "category": ProductCategory.BEBIDA,
            "track_stock": True,
            "stock_quantity": 100,
            "min_stock_level": 20,
            "max_stock_level": 150,
            "reorder_point": 30,
            "unit": "lata",
            "barcode": "1234567890132",
            "sku": "BEB-003"
        },
        
        # Alcohol
        {
            "name": "Cerveza Águila",
            "description": "Cerveza Águila 330ml",
            "price": Decimal("4000"),
            "cost_price": Decimal("1800"),
            "category": ProductCategory.ALCOHOL,
            "track_stock": True,
            "stock_quantity": 80,
            "min_stock_level": 15,
            "max_stock_level": 120,
            "reorder_point": 25,
            "unit": "botella",
            "barcode": "1234567890133",
            "sku": "ALC-001"
        },
        {
            "name": "Vino Tinto Casa",
            "description": "Vino tinto de la casa por copa",
            "price": Decimal("8000"),
            "cost_price": Decimal("3500"),
            "category": ProductCategory.ALCOHOL,
            "track_stock": True,
            "stock_quantity": 25,
            "min_stock_level": 5,
            "max_stock_level": 40,
            "reorder_point": 8,
            "unit": "copa",
            "barcode": "1234567890134",
            "sku": "ALC-002"
        }
    ]
    
    products = []
    for i, product_data in enumerate(products_data):
        existing_product = db.query(Product).filter(Product.name == product_data["name"]).first()
        if not existing_product:
            # Asignar proveedor aleatorio
            product_data["supplier_id"] = random.choice(suppliers).id
            product = Product(**product_data)
            db.add(product)
            products.append(product)
            print(f"   ✅ Producto creado: {product_data['name']} - ${product_data['price']}")
    
    db.commit()
    return products


def create_test_tables(db):
    """Crear mesas de prueba"""
    print("🪑 Creando mesas de prueba...")
    
    tables_data = [
        {"table_number": 1, "capacity": 4, "status": TableStatus.AVAILABLE},
        {"table_number": 2, "capacity": 4, "status": TableStatus.AVAILABLE},
        {"table_number": 3, "capacity": 6, "status": TableStatus.AVAILABLE},
        {"table_number": 4, "capacity": 2, "status": TableStatus.AVAILABLE},
        {"table_number": 5, "capacity": 4, "status": TableStatus.AVAILABLE},
        {"table_number": 6, "capacity": 8, "status": TableStatus.AVAILABLE},
        {"table_number": 7, "capacity": 4, "status": TableStatus.AVAILABLE},
        {"table_number": 8, "capacity": 6, "status": TableStatus.AVAILABLE}
    ]
    
    tables = []
    for table_data in tables_data:
        existing_table = db.query(Table).filter(Table.table_number == table_data["table_number"]).first()
        if not existing_table:
            table = Table(**table_data)
            db.add(table)
            tables.append(table)
            print(f"   ✅ Mesa creada: Mesa {table_data['table_number']} ({table_data['capacity']} personas)")
    
    db.commit()
    return tables


def create_test_customers(db):
    """Crear clientes de prueba"""
    print("👤 Creando clientes de prueba...")
    
    customers_data = [
        {
            "name": "Juan Pérez",
            "email": "juan.perez@email.com",
            "phone": "300-111-2222",
            "address": "Calle 123 #45-67, Bogotá"
        },
        {
            "name": "María García",
            "email": "maria.garcia@email.com",
            "phone": "310-333-4444",
            "address": "Carrera 78 #90-12, Medellín"
        },
        {
            "name": "Carlos López",
            "email": "carlos.lopez@email.com",
            "phone": "315-555-6666",
            "address": "Calle 45 #67-89, Cali"
        },
        {
            "name": "Ana Rodríguez",
            "email": "ana.rodriguez@email.com",
            "phone": "320-777-8888",
            "address": "Carrera 12 #34-56, Barranquilla"
        },
        {
            "name": "Luis Martínez",
            "email": "luis.martinez@email.com",
            "phone": "325-999-0000",
            "address": "Calle 90 #12-34, Bucaramanga"
        }
    ]
    
    customers = []
    for customer_data in customers_data:
        existing_customer = db.query(Customer).filter(Customer.email == customer_data["email"]).first()
        if not existing_customer:
            customer = Customer(**customer_data)
            db.add(customer)
            customers.append(customer)
            print(f"   ✅ Cliente creado: {customer_data['name']}")
    
    db.commit()
    return customers


def create_test_orders(db, users, products, tables, customers):
    """Crear pedidos de prueba"""
    print("📋 Creando pedidos de prueba...")
    
    # Obtener meseros
    waiters = [user for user in users if user.role == UserRole.MESERO]
    
    # Crear pedidos para los últimos 7 días
    for day in range(7):
        order_date = datetime.now() - timedelta(days=day)
        
        # Crear entre 5 y 15 pedidos por día
        num_orders = random.randint(5, 15)
        
        for order_num in range(num_orders):
            # Hora aleatoria del día (entre 11:00 y 22:00)
            hour = random.randint(11, 22)
            minute = random.randint(0, 59)
            order_time = order_date.replace(hour=hour, minute=minute)
            
            # Seleccionar mesa aleatoria
            table = random.choice(tables)
            
            # Seleccionar mesero aleatorio
            waiter = random.choice(waiters)
            
            # Seleccionar cliente aleatorio (o None para walk-ins)
            customer = random.choice([None] + customers)
            
            # Crear pedido
            order = Order(
                order_number=f"ORD-{order_date.strftime('%Y%m%d')}-{order_num+1:03d}",
                table_id=table.id,
                waiter_id=waiter.id,
                customer_id=customer.id if customer else None,
                order_type=OrderType.DINE_IN,
                status=random.choice([OrderStatus.PAID, OrderStatus.SERVED, OrderStatus.READY, OrderStatus.PREPARING]),
                notes=random.choice([None, "Sin cebolla", "Bien cocido", "Extra salsa", "Para llevar"])
            )
            
            db.add(order)
            db.flush()  # Para obtener el ID del pedido
            
            # Agregar items al pedido
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.price,
                    total_price=product.price * quantity,
                    notes=random.choice([None, "Sin hielo", "Extra queso", "Bien hecho"])
                )
                db.add(order_item)
            
            # Calcular totales
            order.calculate_totals()
            
            # Establecer timestamps
            order.created_at = order_time
            if order.status in [OrderStatus.READY, OrderStatus.SERVED, OrderStatus.PAID]:
                order.kitchen_start_time = order_time + timedelta(minutes=random.randint(5, 15))
                order.kitchen_end_time = order_time + timedelta(minutes=random.randint(20, 45))
            if order.status in [OrderStatus.SERVED, OrderStatus.PAID]:
                order.served_at = order_time + timedelta(minutes=random.randint(45, 90))
            if order.status == OrderStatus.PAID:
                order.paid_at = order_time + timedelta(minutes=random.randint(90, 120))
            
            print(f"   ✅ Pedido creado: {order.order_number} - Mesa {table.table_number} - ${order.final_amount}")
    
    db.commit()


def create_test_inventory_locations(db):
    """Crear ubicaciones de inventario"""
    print("🏪 Creando ubicaciones de inventario...")
    
    locations_data = [
        {"name": "Almacén Principal", "description": "Almacén principal del restaurante"},
        {"name": "Refrigerador", "description": "Refrigerador para productos frescos"},
        {"name": "Congelador", "description": "Congelador para productos congelados"},
        {"name": "Bar", "description": "Bar para bebidas y licores"}
    ]
    
    locations = []
    for location_data in locations_data:
        existing_location = db.query(InventoryLocation).filter(InventoryLocation.name == location_data["name"]).first()
        if not existing_location:
            location = InventoryLocation(**location_data)
            db.add(location)
            locations.append(location)
            print(f"   ✅ Ubicación creada: {location_data['name']}")
    
    db.commit()
    return locations


def create_test_inventory_lots(db, products, suppliers, locations):
    """Crear lotes de inventario"""
    print("📦 Creando lotes de inventario...")
    
    for product in products:
        if product.track_stock:
            # Crear 1-3 lotes por producto
            num_lots = random.randint(1, 3)
            
            for lot_num in range(num_lots):
                # Fecha de fabricación (entre 1 y 30 días atrás)
                manufacturing_date = datetime.now().date() - timedelta(days=random.randint(1, 30))
                
                # Fecha de caducidad (entre 7 y 365 días en el futuro)
                expiration_date = manufacturing_date + timedelta(days=random.randint(7, 365))
                
                lot = InventoryLot(
                    product_id=product.id,
                    location_id=random.choice(locations).id,
                    supplier_id=product.supplier_id,
                    lot_number=f"LOT-{product.sku}-{lot_num+1:03d}",
                    batch_number=f"BATCH-{manufacturing_date.strftime('%Y%m%d')}",
                    quantity=random.randint(10, 50),
                    unit_cost=product.cost_price,
                    manufacturing_date=manufacturing_date,
                    expiration_date=expiration_date,
                    purchase_order=f"PO-{manufacturing_date.strftime('%Y%m%d')}",
                    invoice_number=f"INV-{random.randint(1000, 9999)}"
                )
                
                db.add(lot)
                print(f"   ✅ Lote creado: {lot.lot_number} - {product.name}")
    
    db.commit()


def main():
    """Función principal"""
    print("🚀 Creando datos de prueba mejorados para el Sistema POS...")
    
    # Crear tablas si no existen
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Crear datos de prueba
        create_test_users(db)
        suppliers = create_test_suppliers(db)
        products = create_test_products(db, suppliers)
        tables = create_test_tables(db)
        customers = create_test_customers(db)
        create_test_orders(db, db.query(User).all(), products, tables, customers)
        
        # Crear inventario
        locations = create_test_inventory_locations(db)
        create_test_inventory_lots(db, products, suppliers, locations)
        
        print("\n✅ Datos de prueba creados exitosamente!")
        print("\n📊 Resumen:")
        print(f"   👥 Usuarios: {db.query(User).count()}")
        print(f"   🏪 Proveedores: {db.query(Supplier).count()}")
        print(f"   🍽️ Productos: {db.query(Product).count()}")
        print(f"   🪑 Mesas: {db.query(Table).count()}")
        print(f"   👤 Clientes: {db.query(Customer).count()}")
        print(f"   📋 Pedidos: {db.query(Order).count()}")
        print(f"   📦 Lotes: {db.query(InventoryLot).count()}")
        
        print("\n🔑 Credenciales de acceso:")
        print("   Admin: admin / admin123")
        print("   Mesero: maria / maria123")
        print("   Cocina: chef / chef123")
        print("   Caja: caja / caja123")
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
