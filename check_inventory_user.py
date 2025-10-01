#!/usr/bin/env python3
"""
Script para verificar el usuario de inventario
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User, UserRole

def check_inventory_user():
    """Verificar información del usuario de inventario"""
    try:
        print("🔍 Verificando usuario de inventario...")
        
        db = SessionLocal()
        
        try:
            # Buscar el usuario
            user = db.query(User).filter(User.username == 'adminana').first()
            
            if not user:
                print("❌ Usuario 'adminana' no encontrado")
                print("📋 Usuarios existentes:")
                users = db.query(User).all()
                for u in users:
                    print(f"   - {u.username} ({u.role}) - {u.email}")
                return False
            
            print("✅ Usuario encontrado:")
            print(f"   Usuario: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Nombre completo: {user.full_name}")
            print(f"   Rol: {user.role}")
            print(f"   Activo: {user.is_active}")
            print(f"   Verificado: {user.is_verified}")
            print(f"   Creado: {user.created_at}")
            print(f"   Último login: {user.last_login}")
            
            return True
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error verificando usuario: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando usuario de inventario...")
    
    success = check_inventory_user()
    
    if success:
        print("✅ Usuario verificado exitosamente")
    else:
        print("❌ Error verificando usuario")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


