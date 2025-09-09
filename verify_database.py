#!/usr/bin/env python3
"""
Script para verificar que la base de datos esté correctamente configurada
Uso: python verify_database.py
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

def verify_database():
    """Verificar que la base de datos esté correctamente configurada"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        print(f"🔗 Conectando a: {database_url.split('@')[1] if '@' in database_url else 'base de datos local'}")
        
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("🔍 Verificando estructura de la base de datos...")
        
        # Verificar tablas principales
        required_tables = ['users', 'products', 'categories', 'inventory_movements']
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"📋 Tablas existentes: {', '.join(existing_tables)}")
        
        for table in required_tables:
            if table in existing_tables:
                print(f"✅ Tabla {table} existe")
            else:
                print(f"❌ Tabla {table} NO existe")
                return False
        
        # Verificar columnas críticas en users
        users_columns = [col['name'] for col in inspector.get_columns('users')]
        required_users_columns = ['id', 'username', 'email', 'hashed_password', 'is_admin', 'is_active']
        
        print(f"👤 Columnas en users: {', '.join(users_columns)}")
        for col in required_users_columns:
            if col in users_columns:
                print(f"✅ Columna users.{col} existe")
            else:
                print(f"❌ Columna users.{col} NO existe")
                return False
        
        # Verificar columnas críticas en products
        products_columns = [col['name'] for col in inspector.get_columns('products')]
        required_products_columns = ['id', 'name', 'price', 'product_type', 'stock_quantity', 'is_active']
        
        print(f"📦 Columnas en products: {', '.join(products_columns)}")
        for col in required_products_columns:
            if col in products_columns:
                print(f"✅ Columna products.{col} existe")
            else:
                print(f"❌ Columna products.{col} NO existe")
                return False
        
        # Verificar usuario admin
        result = session.execute(text("SELECT username, is_admin, is_active FROM users WHERE username = 'admin'"))
        admin_user = result.fetchone()
        
        if admin_user:
            print(f"✅ Usuario admin encontrado: {admin_user[0]} (admin: {admin_user[1]}, activo: {admin_user[2]})")
        else:
            print("❌ Usuario admin NO encontrado")
            return False
        
        print("🎉 ¡Base de datos verificada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Función principal"""
    print("🔍 Verificación de Base de Datos - Sistema POS")
    print("=" * 50)
    
    if verify_database():
        print("\n✅ Base de datos está correctamente configurada")
        return True
    else:
        print("\n❌ Base de datos necesita migración")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
