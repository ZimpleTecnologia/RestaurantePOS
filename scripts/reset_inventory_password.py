#!/usr/bin/env python3
"""
Script para resetear la contraseña del usuario de inventario
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.auth.security import get_password_hash

def reset_inventory_password():
    """Resetear contraseña del usuario de inventario"""
    try:
        print("🔧 Reseteando contraseña del usuario de inventario...")
        
        db = SessionLocal()
        
        try:
            # Buscar el usuario
            user = db.query(User).filter(User.username == 'adminana').first()
            
            if not user:
                print("❌ Usuario 'adminana' no encontrado")
                return False
            
            # Nueva contraseña
            new_password = "admin123"
            hashed_password = get_password_hash(new_password)
            
            # Actualizar contraseña
            user.hashed_password = hashed_password
            db.commit()
            
            print("✅ Contraseña actualizada exitosamente")
            print(f"   Usuario: adminana")
            print(f"   Nueva contraseña: {new_password}")
            print(f"   Rol: {user.role}")
            print(f"   Email: {user.email}")
            
            return True
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error actualizando contraseña: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Reseteando contraseña del usuario de inventario...")
    
    success = reset_inventory_password()
    
    if success:
        print("✅ Contraseña actualizada exitosamente")
    else:
        print("❌ Error actualizando contraseña")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


