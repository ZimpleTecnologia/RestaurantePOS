#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar columnas faltantes
Uso: python migrate_database.py
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """Obtener URL de base de datos desde variables de entorno"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://sistema_pos_user:password@localhost:5432/restaurante_pos"
    )

def check_column_exists(engine, table_name, column_name):
    """Verificar si una columna existe en una tabla"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        print(f"⚠️  Error verificando columna {column_name} en {table_name}: {e}")
        return False

def migrate_database():
    """Migrar la base de datos agregando columnas faltantes"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        print(f"🔗 Conectando a: {database_url.split('@')[1] if '@' in database_url else 'base de datos local'}")
        
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("🔍 Verificando estructura de la base de datos...")
        
        # Verificar y agregar columnas faltantes en la tabla users
        users_columns_to_add = [
            ("is_admin", "BOOLEAN DEFAULT FALSE"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("full_name", "VARCHAR(100)"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for column_name, column_definition in users_columns_to_add:
            if not check_column_exists(engine, "users", column_name):
                print(f"➕ Agregando columna {column_name} a la tabla users...")
                session.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_definition}"))
                session.commit()
                print(f"✅ Columna {column_name} agregada exitosamente")
            else:
                print(f"✅ Columna {column_name} ya existe")
        
        # Verificar y agregar columnas faltantes en la tabla products
        products_columns_to_add = [
            ("supplier", "VARCHAR(100)"),
            ("product_type", "VARCHAR(20) DEFAULT 'inventory'"),
            ("stock_quantity", "DECIMAL(10,2) DEFAULT 0"),
            ("min_stock_level", "DECIMAL(10,2) DEFAULT 0"),
            ("purchase_price", "DECIMAL(10,2)"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for column_name, column_definition in products_columns_to_add:
            if not check_column_exists(engine, "products", column_name):
                print(f"➕ Agregando columna {column_name} a la tabla products...")
                session.execute(text(f"ALTER TABLE products ADD COLUMN {column_name} {column_definition}"))
                session.commit()
                print(f"✅ Columna {column_name} agregada exitosamente")
            else:
                print(f"✅ Columna {column_name} ya existe")
        
        # Verificar y agregar columnas faltantes en la tabla categories
        categories_columns_to_add = [
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for column_name, column_definition in categories_columns_to_add:
            if not check_column_exists(engine, "categories", column_name):
                print(f"➕ Agregando columna {column_name} a la tabla categories...")
                session.execute(text(f"ALTER TABLE categories ADD COLUMN {column_name} {column_definition}"))
                session.commit()
                print(f"✅ Columna {column_name} agregada exitosamente")
            else:
                print(f"✅ Columna {column_name} ya existe")
        
        # Crear tabla inventory_movements si no existe
        print("🔍 Verificando tabla inventory_movements...")
        try:
            session.execute(text("SELECT 1 FROM inventory_movements LIMIT 1"))
            print("✅ Tabla inventory_movements ya existe")
        except Exception:
            print("➕ Creando tabla inventory_movements...")
            session.execute(text("""
                CREATE TABLE inventory_movements (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER REFERENCES products(id),
                    user_id INTEGER REFERENCES users(id),
                    movement_type VARCHAR(20) NOT NULL,
                    quantity DECIMAL(10,2) NOT NULL,
                    adjustment_type VARCHAR(20),
                    reason VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            session.commit()
            print("✅ Tabla inventory_movements creada exitosamente")
        
        # Actualizar usuarios existentes para que tengan is_admin = true si es admin
        print("🔄 Actualizando usuarios existentes...")
        session.execute(text("""
            UPDATE users 
            SET is_admin = true, is_active = true
            WHERE username = 'admin' OR username = 'administrator'
        """))
        session.commit()
        
        print("🎉 ¡Migración completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Función principal"""
    print("🔄 Migración de Base de Datos - Sistema POS")
    print("=" * 50)
    
    try:
        if migrate_database():
            print("\n✅ Migración completada exitosamente")
            print("🚀 La base de datos está actualizada y lista para usar")
            return True
        else:
            print("\n❌ Error durante la migración")
            return False
    except Exception as e:
        print(f"\n❌ Error crítico durante la migración: {e}")
        return False

if __name__ == "__main__":
    main()
