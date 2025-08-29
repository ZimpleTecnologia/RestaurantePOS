#!/usr/bin/env python3
"""
Script para inicializar usuarios con diferentes roles
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.auth.security import get_password_hash

def create_users():
    """Crear usuarios con diferentes roles"""
    db = SessionLocal()
    
    try:
        # Verificar usuarios existentes
        existing_users = db.query(User).all()
        existing_usernames = [user.username for user in existing_users]
        
        if existing_users:
            print("⚠️  Usuarios existentes en la base de datos:")
            for user in existing_users:
                print(f"  - {user.username} ({user.role})")
            print()
        
        # Crear usuarios con diferentes roles
        users_data = [
            {
                "username": "admin",
                "email": "admin@restaurante.com",
                "full_name": "Administrador del Sistema",
                "password": "admin123",
                "role": UserRole.ADMIN
            },
            {
                "username": "supervisor",
                "email": "supervisor@restaurante.com",
                "full_name": "Supervisor General",
                "password": "super123",
                "role": UserRole.SUPERVISOR
            },
            {
                "username": "mesero1",
                "email": "mesero1@restaurante.com",
                "full_name": "Juan Pérez - Mesero",
                "password": "mesero123",
                "role": UserRole.MESERO
            },
            {
                "username": "mesero2",
                "email": "mesero2@restaurante.com",
                "full_name": "María García - Mesera",
                "password": "mesero123",
                "role": UserRole.MESERO
            },
            {
                "username": "cocina",
                "email": "cocina@restaurante.com",
                "full_name": "Chef Carlos López",
                "password": "cocina123",
                "role": UserRole.COCINA
            },
            {
                "username": "caja",
                "email": "caja@restaurante.com",
                "full_name": "Ana Martínez - Cajera",
                "password": "caja123",
                "role": UserRole.CAJA
            },
            {
                "username": "almacen",
                "email": "almacen@restaurante.com",
                "full_name": "Roberto Silva - Almacén",
                "password": "almacen123",
                "role": UserRole.ALMACEN
            }
        ]
        
        created_users = []
        
        for user_data in users_data:
            # Verificar si el usuario ya existe
            if user_data["username"] in existing_usernames:
                print(f"⚠️  Usuario {user_data['username']} ya existe, saltando...")
                continue
            
            # Crear hash de la contraseña
            hashed_password = get_password_hash(user_data["password"])
            
            # Crear usuario
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
            created_users.append(user_data)
        
        # Confirmar cambios
        db.commit()
        
        print("✅ Usuarios creados exitosamente:")
        print()
        print("📋 Credenciales de acceso:")
        print("=" * 50)
        
        for user_data in created_users:
            role_display = {
                UserRole.ADMIN: "Administrador",
                UserRole.SUPERVISOR: "Supervisor", 
                UserRole.MESERO: "Mesero",
                UserRole.COCINA: "Cocina",
                UserRole.CAJA: "Caja",
                UserRole.ALMACEN: "Almacén"
            }.get(user_data["role"], user_data["role"])
            
            print(f"👤 {user_data['full_name']}")
            print(f"   Usuario: {user_data['username']}")
            print(f"   Contraseña: {user_data['password']}")
            print(f"   Rol: {role_display}")
            print(f"   Email: {user_data['email']}")
            print()
        
        print("=" * 50)
        print("🎯 Módulos accesibles por rol:")
        print()
        print("👑 ADMIN: Todos los módulos")
        print("👨‍💼 SUPERVISOR: Dashboard, Ventas, Productos, Mesas, Pedidos, Cocina, Inventario, Caja y Ventas, Reportes")
        print("👨‍🍳 MESERO: Pedidos, Mesas")
        print("🔥 COCINA: Cocina")
        print("💰 CAJA: Caja y Ventas, Ventas")
        print("📦 ALMACÉN: Inventario, Productos")
        print()
        print("🚀 Para probar el sistema:")
        print("1. Inicia la aplicación: python -m uvicorn app.main:app --reload")
        print("2. Ve a: http://localhost:8000/login")
        print("3. Usa las credenciales de arriba para probar diferentes roles")
        
    except Exception as e:
        print(f"❌ Error creando usuarios: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Inicializando usuarios del sistema...")
    create_users()
