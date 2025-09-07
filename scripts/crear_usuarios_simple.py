#!/usr/bin/env python3
"""
Script simple para crear usuarios uno por uno
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.auth.security import get_password_hash

def crear_usuarios():
    """Crear usuarios uno por uno"""
    db = SessionLocal()
    
    try:
        # Lista de usuarios a crear
        usuarios = [
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
            },
            {
                "username": "supervisor",
                "email": "supervisor@restaurante.com",
                "full_name": "Supervisor General",
                "password": "super123",
                "role": UserRole.SUPERVISOR
            }
        ]
        
        usuarios_creados = []
        
        for user_data in usuarios:
            # Verificar si el usuario ya existe
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            
            if existing_user:
                print(f"⚠️  Usuario {user_data['username']} ya existe")
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
            db.commit()
            usuarios_creados.append(user_data)
            print(f"✅ Usuario {user_data['username']} creado exitosamente")
        
        if usuarios_creados:
            print(f"\n🎉 Se crearon {len(usuarios_creados)} usuarios exitosamente")
            print("\n📋 Credenciales de acceso:")
            print("=" * 50)
            
            for user_data in usuarios_creados:
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
        else:
            print("ℹ️  Todos los usuarios ya existen")
        
    except Exception as e:
        print(f"❌ Error creando usuarios: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creando usuarios del sistema...")
    crear_usuarios()
