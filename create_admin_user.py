#!/usr/bin/env python3
"""
Script para crear un usuario administrador y categoría por defecto en la base de datos
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User, UserRole
from app.models.product import Category
from app.auth.security import get_password_hash

# Configuración de la base de datos
DATABASE_URL = "postgresql://sistema_pos_user:sistema_pos_password@postgres:5432/sistema_pos"

def create_admin_user_and_category():
    """Crear usuario administrador y categoría por defecto"""
    try:
        print("🔍 Conectando a la base de datos...")
        engine = create_engine(DATABASE_URL)
        
        # Crear tablas si no existen
        Base.metadata.create_all(bind=engine)
        
        # Crear sesión
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Verificar si ya existe un usuario admin
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✅ Usuario administrador ya existe")
            print(f"   Usuario: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Rol: {existing_admin.role}")
        else:
            # Crear usuario administrador
            admin_user = User(
                username="admin",
                email="admin@sistema-pos.com",
                full_name="Administrador del Sistema",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print("✅ Usuario administrador creado exitosamente")
            print(f"   Usuario: {admin_user.username}")
            print(f"   Contraseña: admin123")
            print(f"   Email: {admin_user.email}")
            print(f"   Rol: {admin_user.role}")
        
        # Verificar si ya existe una categoría por defecto
        existing_category = db.query(Category).filter(Category.name == "General").first()
        if existing_category:
            print("✅ Categoría 'General' ya existe")
            print(f"   ID: {existing_category.id}")
            print(f"   Nombre: {existing_category.name}")
        else:
            # Crear categoría por defecto
            default_category = Category(
                name="General",
                description="Categoría general para productos sin clasificación específica",
                is_active=True
            )
            
            db.add(default_category)
            db.commit()
            db.refresh(default_category)
            
            print("✅ Categoría 'General' creada exitosamente")
            print(f"   ID: {default_category.id}")
            print(f"   Nombre: {default_category.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear usuario administrador y categoría: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = create_admin_user_and_category()
    sys.exit(0 if success else 1)
