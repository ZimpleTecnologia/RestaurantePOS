#!/usr/bin/env python3
"""
Script para crear usuario administrador de inventario
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal, create_tables
from app.models.user import User, UserRole
from app.auth.security import get_password_hash

def create_inventory_admin():
    """Crear usuario administrador de inventario"""
    try:
        print("🔧 Creando usuario administrador de inventario...")
        
        # Crear tablas si no existen
        create_tables()
        
        db = SessionLocal()
        
        try:
            # Verificar si ya existe el usuario
            existing_user = db.query(User).filter(User.username == 'adminana').first()
            if existing_user:
                print("✅ Usuario adminana ya existe")
                return True
            
            # Crear hash de contraseña
            password = "54321"
            hashed_password = get_password_hash(password)
            
            # Crear usuario administrador de inventario
            inventory_admin = User(
                username='adminana',
                email='adminana@sistema.com',
                full_name='Administrador de Inventario',
                hashed_password=hashed_password,
                role=UserRole.ALMACEN,  # Usar rol ALMACEN para inventario
                is_active=True,
                is_verified=True
            )
            
            db.add(inventory_admin)
            db.commit()
            db.refresh(inventory_admin)
            
            print("✅ Usuario administrador de inventario creado exitosamente")
            print(f"   Usuario: adminana")
            print(f"   Contraseña: {password}")
            print(f"   Rol: {inventory_admin.role}")
            print(f"   Email: {inventory_admin.email}")
            
            return True
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Creando usuario administrador de inventario...")
    
    success = create_inventory_admin()
    
    if success:
        print("✅ Usuario creado exitosamente")
    else:
        print("❌ Error creando usuario")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
