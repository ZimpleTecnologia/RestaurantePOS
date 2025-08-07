#!/usr/bin/env python3
"""
Script para crear un usuario administrador por defecto
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db, create_tables
from app.models.user import User, UserRole
from app.auth.security import get_password_hash
from app.config import settings

def create_admin_user():
    """Crear usuario administrador por defecto"""
    print("🔧 Creando usuario administrador por defecto...")
    
    # Crear tablas si no existen
    create_tables()
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Verificar si ya existe un usuario admin
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin:
            print("✅ Usuario admin ya existe")
            print(f"   Usuario: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Rol: {existing_admin.role}")
            return existing_admin
        
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
        
        print("✅ Usuario administrador creado exitosamente!")
        print(f"   Usuario: {admin_user.username}")
        print(f"   Contraseña: admin123")
        print(f"   Email: {admin_user.email}")
        print(f"   Rol: {admin_user.role}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error al crear usuario admin: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_test_users():
    """Crear usuarios de prueba adicionales"""
    print("\n🔧 Creando usuarios de prueba...")
    
    db = next(get_db())
    
    try:
        # Usuario vendedor
        vendedor = User(
            username="vendedor",
            email="vendedor@sistema-pos.com",
            full_name="Vendedor Ejemplo",
            hashed_password=get_password_hash("vendedor123"),
            role=UserRole.VENDEDOR,
            is_active=True,
            is_verified=True
        )
        
        # Usuario caja
        caja = User(
            username="caja",
            email="caja@sistema-pos.com",
            full_name="Cajero Ejemplo",
            hashed_password=get_password_hash("caja123"),
            role=UserRole.CAJA,
            is_active=True,
            is_verified=True
        )
        
        # Verificar si ya existen
        existing_vendedor = db.query(User).filter(User.username == "vendedor").first()
        existing_caja = db.query(User).filter(User.username == "caja").first()
        
        if not existing_vendedor:
            db.add(vendedor)
            print("✅ Usuario vendedor creado (vendedor/vendedor123)")
        
        if not existing_caja:
            db.add(caja)
            print("✅ Usuario caja creado (caja/caja123)")
        
        db.commit()
        print("✅ Usuarios de prueba creados exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al crear usuarios de prueba: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Iniciando creación de usuarios por defecto...")
    
    # Crear usuario admin
    create_admin_user()
    
    # Crear usuarios de prueba
    create_test_users()
    
    print("\n🎉 Proceso completado!")
    print("\n📋 Credenciales disponibles:")
    print("   Admin: admin / admin123")
    print("   Vendedor: vendedor / vendedor123")
    print("   Caja: caja / caja123")
