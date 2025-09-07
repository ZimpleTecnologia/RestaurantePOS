#!/usr/bin/env python3
"""
Script completo para crear datos de prueba del Sistema POS
Cubre todas las funcionalidades: usuarios, productos, ventas, clientes, etc.
"""
import sys
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db, create_tables
from app.models.user import User, UserRole
from app.models.product import Product, ProductType, Category, SubCategory
from app.models.customer import Customer, Credit, Payment
from app.models.supplier import Supplier, Purchase, PurchaseItem
from app.models.location import Location, Table, TableStatus, LocationType
from app.models.sale import Sale, SaleItem, PaymentMethod, SaleStatus
from app.models.order import Order, OrderItem, OrderStatus, OrderPriority
from app.models.inventory import InventoryMovement, MovementType
from app.models.recipe import Recipe, RecipeItem
from app.models.settings import SystemSettings
from app.auth.security import get_password_hash

def create_users():
    """Crear usuarios de prueba para todos los roles"""
    print("👥 Creando usuarios de prueba...")
    
    db = next(get_db())
    
    users_data = [
        # Administradores
        {
            "username": "admin",
            "email": "admin@restaurante.com",
            "full_name": "Administrador Principal",
            "password": "admin123",
            "role": UserRole.ADMIN
        },
        {
            "username": "supervisor",
            "email": "supervisor@restaurante.com",
            "full_name": "María Supervisor",
            "password": "super123",
            "role": UserRole.SUPERVISOR
        },
        
        # Meseros
        {
            "username": "mesero1",
            "email": "juan@restaurante.com",
            "full_name": "Juan Pérez",
            "password": "mesero123",
            "role": UserRole.MESERO
        },
        {
            "username": "mesero2",
            "email": "maria@restaurante.com",
            "full_name": "María García",
            "password": "mesero123",
            "role": UserRole.MESERO
        },
        {
            "username": "mesero3",
            "email": "carlos@restaurante.com",
            "full_name": "Carlos López",
            "password": "mesero123",
            "role": UserRole.MESERO
        },
        
        # Cocina
        {
            "username": "cocinero1",
            "email": "chef1@restaurante.com",
            "full_name": "Chef Roberto",
            "password": "cocina123",
            "role": UserRole.COCINA
        },
        {
            "username": "cocinero2",
            "email": "chef2@restaurante.com",
            "full_name": "Chef Ana",
            "password": "cocina123",
            "role": UserRole.COCINA
        },
        
        # Caja
        {
            "username": "caja1",
            "email": "caja1@restaurante.com",
            "full_name": "Cajero Pedro",
            "password": "caja123",
            "role": UserRole.CAJA
        },
        {
            "username": "caja2",
            "email": "caja2@restaurante.com",
            "full_name": "Cajera Laura",
            "password": "caja123",
            "role": UserRole.CAJA
        },
        
        # Almacén
        {
            "username": "almacen1",
            "email": "almacen@restaurante.com",
            "full_name": "Encargado Almacén",
            "password": "almacen123",
            "role": UserRole.ALMACEN
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                is_active=True,
                is_verified=True
            )
            db.add(user)
            created_users.append(user)
            print(f"✅ Usuario {user_data['username']} creado")
        else:
            created_users.append(existing_user)
            print(f"ℹ️  Usuario {user_data['username']} ya existe")
    
    db.commit()
    return created_users

def create_categories_and_products():
    """Crear categorías, subcategorías y productos"""
    print("\n🍽️ Creando categorías y productos...")
    
    db = next(get_db())
    
    # Categorías principales
    categories_data = [
        {
            "name": "Platos Principales",
            "description": "Platos fuertes del menú",
            "subcategories": [
                {
                    "name": "Carnes",
                    "products": [
                        {"code": "CAR001", "name": "Bistec a la Plancha", "price": 25.00, "cost_price": 12.00, "stock": 50},
                        {"code": "CAR002", "name": "Pollo Asado", "price": 18.00, "cost_price": 8.00, "stock": 30},
                        {"code": "CAR003", "name": "Cerdo Ahumado", "price": 22.00, "cost_price": 10.00, "stock": 25}
                    ]
                },
                {
                    "name": "Pescados",
                    "products": [
                        {"code": "PES001", "name": "Salmón a la Parrilla", "price": 28.00, "cost_price": 15.00, "stock": 20},
                        {"code": "PES002", "name": "Trucha Frita", "price": 20.00, "cost_price": 9.00, "stock": 15}
                    ]
                }
            ]
        },
        {
            "name": "Entradas",
            "description": "Platos de entrada",
            "subcategories": [
                {
                    "name": "Ensaladas",
                    "products": [
                        {"code": "ENS001", "name": "Ensalada César", "price": 12.00, "cost_price": 5.00, "stock": 40},
                        {"code": "ENS002", "name": "Ensalada Griega", "price": 10.00, "cost_price": 4.00, "stock": 35}
                    ]
                },
                {
                    "name": "Sopas",
                    "products": [
                        {"code": "SOP001", "name": "Sopa de Pollo", "price": 8.00, "cost_price": 3.00, "stock": 60},
                        {"code": "SOP002", "name": "Sopa de Tomate", "price": 7.00, "cost_price": 2.50, "stock": 55}
                    ]
                }
            ]
        },
        {
            "name": "Bebidas",
            "description": "Bebidas y refrescos",
            "subcategories": [
                {
                    "name": "Refrescos",
                    "products": [
                        {"code": "REF001", "name": "Coca Cola", "price": 3.00, "cost_price": 1.20, "stock": 100},
                        {"code": "REF002", "name": "Sprite", "price": 3.00, "cost_price": 1.20, "stock": 80},
                        {"code": "REF003", "name": "Fanta", "price": 3.00, "cost_price": 1.20, "stock": 75}
                    ]
                },
                {
                    "name": "Jugos",
                    "products": [
                        {"code": "JUG001", "name": "Jugo de Naranja", "price": 4.00, "cost_price": 1.50, "stock": 50},
                        {"code": "JUG002", "name": "Limonada", "price": 3.50, "cost_price": 1.00, "stock": 45}
                    ]
                }
            ]
        },
        {
            "name": "Postres",
            "description": "Postres y dulces",
            "subcategories": [
                {
                    "name": "Helados",
                    "products": [
                        {"code": "HEL001", "name": "Helado de Vainilla", "price": 5.00, "cost_price": 2.00, "stock": 30},
                        {"code": "HEL002", "name": "Helado de Chocolate", "price": 5.00, "cost_price": 2.00, "stock": 30}
                    ]
                },
                {
                    "name": "Pasteles",
                    "products": [
                        {"code": "PAS001", "name": "Torta de Chocolate", "price": 8.00, "cost_price": 3.50, "stock": 20},
                        {"code": "PAS002", "name": "Flan Casero", "price": 6.00, "cost_price": 2.50, "stock": 25}
                    ]
                }
            ]
        }
    ]
    
    created_products = []
    
    for cat_data in categories_data:
        # Crear categoría
        category = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not category:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"],
                is_active=True
            )
            db.add(category)
            db.commit()
            db.refresh(category)
            print(f"✅ Categoría '{cat_data['name']}' creada")
        
        for subcat_data in cat_data["subcategories"]:
            # Crear subcategoría
            subcategory = db.query(SubCategory).filter(
                SubCategory.name == subcat_data["name"],
                SubCategory.category_id == category.id
            ).first()
            if not subcategory:
                subcategory = SubCategory(
                    name=subcat_data["name"],
                    category_id=category.id,
                    is_active=True
                )
                db.add(subcategory)
                db.commit()
                db.refresh(subcategory)
                print(f"  ✅ Subcategoría '{subcat_data['name']}' creada")
            
            # Crear productos
            for prod_data in subcat_data["products"]:
                product = db.query(Product).filter(Product.code == prod_data["code"]).first()
                if not product:
                    product = Product(
                        code=prod_data["code"],
                        name=prod_data["name"],
                        price=prod_data["price"],
                        cost_price=prod_data["cost_price"],
                        stock=prod_data["stock"],
                        category_id=category.id,
                        subcategory_id=subcategory.id,
                        product_type=ProductType.PRODUCTO,
                        is_active=True
                    )
                    db.add(product)
                    created_products.append(product)
                    print(f"    ✅ Producto '{prod_data['name']}' creado")
    
    db.commit()
    return created_products

def create_customers():
    """Crear clientes de prueba"""
    print("\n👤 Creando clientes de prueba...")
    
    db = next(get_db())
    
    customers_data = [
        {
            "document_type": "CC",
            "document_number": "12345678",
            "first_name": "Juan",
            "last_name": "González",
            "email": "juan.gonzalez@email.com",
            "phone": "3001234567",
            "address": "Calle 123 #45-67",
            "city": "Bogotá",
            "credit_limit": 1000.00
        },
        {
            "document_type": "CC",
            "document_number": "87654321",
            "first_name": "María",
            "last_name": "Rodríguez",
            "email": "maria.rodriguez@email.com",
            "phone": "3007654321",
            "address": "Carrera 78 #12-34",
            "city": "Medellín",
            "credit_limit": 500.00
        },
        {
            "document_type": "CE",
            "document_number": "98765432",
            "first_name": "Carlos",
            "last_name": "López",
            "email": "carlos.lopez@email.com",
            "phone": "3009876543",
            "address": "Avenida 5 #23-45",
            "city": "Cali",
            "credit_limit": 750.00
        },
        {
            "document_type": "NIT",
            "document_number": "900123456",
            "first_name": "Restaurante",
            "last_name": "El Buen Sabor",
            "email": "contacto@buensabor.com",
            "phone": "3001112222",
            "address": "Centro Comercial Plaza Mayor",
            "city": "Bogotá",
            "credit_limit": 2000.00
        }
    ]
    
    created_customers = []
    
    for cust_data in customers_data:
        existing_customer = db.query(Customer).filter(
            Customer.document_number == cust_data["document_number"]
        ).first()
        if not existing_customer:
            customer = Customer(
                document_type=cust_data["document_type"],
                document_number=cust_data["document_number"],
                first_name=cust_data["first_name"],
                last_name=cust_data["last_name"],
                email=cust_data["email"],
                phone=cust_data["phone"],
                address=cust_data["address"],
                city=cust_data["city"],
                credit_limit=cust_data["credit_limit"],
                is_active=True
            )
            db.add(customer)
            created_customers.append(customer)
            print(f"✅ Cliente {cust_data['first_name']} {cust_data['last_name']} creado")
        else:
            created_customers.append(existing_customer)
            print(f"ℹ️  Cliente {cust_data['first_name']} {cust_data['last_name']} ya existe")
    
    db.commit()
    return created_customers

def create_suppliers():
    """Crear proveedores de prueba"""
    print("\n🏢 Creando proveedores de prueba...")
    
    db = next(get_db())
    
    suppliers_data = [
        {
            "name": "Distribuidora de Alimentos S.A.",
            "document_type": "NIT",
            "document_number": "800123456",
            "contact_name": "Pedro Distribuidor",
            "email": "pedro@distribuidora.com",
            "phone": "3005556666",
            "address": "Zona Industrial Calle 100",
            "city": "Bogotá",
            "credit_limit": 5000.00,
            "payment_terms": "30 días"
        },
        {
            "name": "Carnes Frescas Ltda.",
            "document_type": "NIT",
            "document_number": "800654321",
            "contact_name": "Ana Carnicera",
            "email": "ana@carnesfrescas.com",
            "phone": "3007778888",
            "address": "Mercado Central Local 15",
            "city": "Bogotá",
            "credit_limit": 3000.00,
            "payment_terms": "15 días"
        },
        {
            "name": "Bebidas y Refrescos",
            "document_type": "NIT",
            "document_number": "800999888",
            "contact_name": "Luis Bebidas",
            "email": "luis@bebidas.com",
            "phone": "3001113333",
            "address": "Bodega 7 Zona Franca",
            "city": "Medellín",
            "credit_limit": 4000.00,
            "payment_terms": "7 días"
        }
    ]
    
    created_suppliers = []
    
    for sup_data in suppliers_data:
        existing_supplier = db.query(Supplier).filter(
            Supplier.document_number == sup_data["document_number"]
        ).first()
        if not existing_supplier:
            supplier = Supplier(
                name=sup_data["name"],
                document_type=sup_data["document_type"],
                document_number=sup_data["document_number"],
                contact_name=sup_data["contact_name"],
                email=sup_data["email"],
                phone=sup_data["phone"],
                address=sup_data["address"],
                city=sup_data["city"],
                credit_limit=sup_data["credit_limit"],
                payment_terms=sup_data["payment_terms"],
                is_active=True
            )
            db.add(supplier)
            created_suppliers.append(supplier)
            print(f"✅ Proveedor {sup_data['name']} creado")
        else:
            created_suppliers.append(existing_supplier)
            print(f"ℹ️  Proveedor {sup_data['name']} ya existe")
    
    db.commit()
    return created_suppliers

def create_locations_and_tables():
    """Crear ubicaciones y mesas"""
    print("\n📍 Creando ubicaciones y mesas...")
    
    db = next(get_db())
    
    # Crear ubicación principal
    location = db.query(Location).filter(Location.name == "Restaurante Principal").first()
    if not location:
        location = Location(
            name="Restaurante Principal",
            description="Ubicación principal del restaurante",
            location_type=LocationType.RESTAURANTE,
            address="Calle 15 #23-45",
            phone="3001234567",
            email="info@restaurante.com",
            manager_name="Gerente Principal",
            capacity=100,
            is_active=True
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        print("✅ Ubicación 'Restaurante Principal' creada")
    
    # Crear mesas
    tables_data = [
        {"table_number": "1", "name": "Mesa 1", "capacity": 4, "status": TableStatus.LIBRE},
        {"table_number": "2", "name": "Mesa 2", "capacity": 4, "status": TableStatus.LIBRE},
        {"table_number": "3", "name": "Mesa 3", "capacity": 6, "status": TableStatus.LIBRE},
        {"table_number": "4", "name": "Mesa 4", "capacity": 6, "status": TableStatus.LIBRE},
        {"table_number": "5", "name": "Mesa 5", "capacity": 2, "status": TableStatus.LIBRE},
        {"table_number": "6", "name": "Mesa 6", "capacity": 2, "status": TableStatus.LIBRE},
        {"table_number": "7", "name": "Mesa 7", "capacity": 8, "status": TableStatus.LIBRE},
        {"table_number": "8", "name": "Mesa 8", "capacity": 8, "status": TableStatus.LIBRE}
    ]
    
    created_tables = []
    
    for table_data in tables_data:
        existing_table = db.query(Table).filter(
            Table.table_number == table_data["table_number"],
            Table.location_id == location.id
        ).first()
        if not existing_table:
            table = Table(
                location_id=location.id,
                table_number=table_data["table_number"],
                name=table_data["name"],
                capacity=table_data["capacity"],
                status=table_data["status"],
                is_active=True
            )
            db.add(table)
            created_tables.append(table)
            print(f"✅ Mesa {table_data['table_number']} creada")
        else:
            created_tables.append(existing_table)
            print(f"ℹ️  Mesa {table_data['table_number']} ya existe")
    
    db.commit()
    return location, created_tables

def create_system_settings():
    """Crear configuraciones del sistema"""
    print("\n⚙️ Creando configuraciones del sistema...")
    
    db = next(get_db())
    
    existing_settings = db.query(SystemSettings).first()
    if not existing_settings:
        settings = SystemSettings(
            company_name="Restaurante El Buen Sabor",
            currency="COP",
            timezone="America/Bogota",
            primary_color="#667eea",
            secondary_color="#764ba2",
            accent_color="#28a745",
            sidebar_color="#667eea",
            app_title="Sistema POS - El Buen Sabor",
            app_subtitle="Punto de Venta",
            print_header="Restaurante El Buen Sabor\nCalle 15 #23-45\nTel: 3001234567",
            print_footer="Gracias por su visita\n¡Vuelva pronto!",
            enable_notifications=True,
            low_stock_threshold=10
        )
        db.add(settings)
        db.commit()
        print("✅ Configuraciones del sistema creadas")
    else:
        print("ℹ️  Configuraciones del sistema ya existen")

def create_sample_sales_and_orders():
    """Crear ventas y órdenes de ejemplo"""
    print("\n💰 Creando ventas y órdenes de ejemplo...")
    
    db = next(get_db())
    
    # Obtener datos necesarios
    users = db.query(User).filter(User.role == UserRole.MESERO).limit(2).all()
    customers = db.query(Customer).limit(2).all()
    tables = db.query(Table).limit(3).all()
    products = db.query(Product).limit(5).all()
    
    if not users or not customers or not tables or not products:
        print("⚠️  No hay suficientes datos para crear ventas de ejemplo")
        return
    
    # Crear algunas ventas de ejemplo
    for i in range(3):
        # Crear venta
        sale = Sale(
            sale_number=f"V{i+1:03d}",
            customer_id=customers[i % len(customers)].id,
            user_id=users[i % len(users)].id,
            table_id=tables[i % len(tables)].id,
            subtotal=Decimal('0.00'),
            tax=Decimal('0.00'),
            discount=Decimal('0.00'),
            total=Decimal('0.00'),
            status=SaleStatus.COMPLETADA,
            created_at=datetime.now() - timedelta(days=i+1)
        )
        db.add(sale)
        db.commit()
        db.refresh(sale)
        
        # Crear items de venta
        total_sale = Decimal('0.00')
        for j in range(random.randint(2, 4)):
            product = products[j % len(products)]
            quantity = random.randint(1, 3)
            unit_price = Decimal(str(product.price))
            total_item = unit_price * quantity
            
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total=total_item
            )
            db.add(sale_item)
            total_sale += total_item
        
        # Actualizar totales de la venta
        sale.subtotal = total_sale
        sale.tax = total_sale * Decimal('0.19')  # 19% IVA
        sale.total = sale.subtotal + sale.tax
        
        # Crear método de pago
        payment_method = PaymentMethod(
            sale_id=sale.id,
            payment_type="efectivo",
            amount=sale.total
        )
        db.add(payment_method)
        
        print(f"✅ Venta {sale.sale_number} creada - Total: ${sale.total}")
    
    db.commit()

def main():
    """Función principal"""
    print("=" * 70)
    print("🎯 CREACIÓN DE DATOS DE PRUEBA - SISTEMA POS")
    print("=" * 70)
    print(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Crear tablas si no existen
        create_tables()
        print("✅ Tablas verificadas")
        
        # Crear datos en orden
        users = create_users()
        products = create_categories_and_products()
        customers = create_customers()
        suppliers = create_suppliers()
        location, tables = create_locations_and_tables()
        create_system_settings()
        create_sample_sales_and_orders()
        
        print("\n" + "=" * 70)
        print("🎉 DATOS DE PRUEBA CREADOS EXITOSAMENTE")
        print("=" * 70)
        print("📊 Resumen de datos creados:")
        print(f"   👥 Usuarios: {len(users)}")
        print(f"   🍽️ Productos: {len(products)}")
        print(f"   👤 Clientes: {len(customers)}")
        print(f"   🏢 Proveedores: {len(suppliers)}")
        print(f"   🪑 Mesas: {len(tables)}")
        print()
        print("🔑 Credenciales de acceso:")
        print("   Admin: admin / admin123")
        print("   Mesero: mesero1 / mesero123")
        print("   Cocina: cocinero1 / cocina123")
        print("   Caja: caja1 / caja123")
        print()
        print("🚀 ¡El sistema está listo para usar!")
        
    except Exception as e:
        print(f"\n❌ Error creando datos de prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
