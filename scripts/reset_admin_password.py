#!/usr/bin/env python3
"""
Script para resetear la contraseña del usuario admin
"""
import sys
import os
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, create_tables
from app.models.user import User, UserRole
from app.auth.security import get_password_hash, verify_password
from app.config import settings

def reset_admin_password():
    """Resetear la contraseña del usuario admin"""
    print("🔧 Reseteando contraseña del usuario admin...")
    
    db = next(get_db())
    
    try:
        # Buscar usuario admin
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("❌ Usuario admin no encontrado")
            return False
        
        # Nueva contraseña
        new_password = "admin123"
        new_hashed_password = get_password_hash(new_password)
        
        # Actualizar contraseña
        admin_user.hashed_password = new_hashed_password
        admin_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Contraseña del admin reseteada exitosamente")
        print(f"   Usuario: {admin_user.username}")
        print(f"   Nueva contraseña: {new_password}")
        print(f"   Email: {admin_user.email}")
        print(f"   Rol: {admin_user.role}")
        
        # Verificar que la nueva contraseña funciona
        if verify_password(new_password, admin_user.hashed_password):
            print("✅ Verificación de nueva contraseña exitosa")
            return True
        else:
            print("❌ Error: La nueva contraseña no se puede verificar")
            return False
        
    except Exception as e:
        print(f"❌ Error reseteando contraseña: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_admin_login():
    """Probar el login del admin con la nueva contraseña"""
    print("\n🔐 Probando login del admin...")
    
    db = next(get_db())
    
    try:
        # Buscar usuario admin
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("❌ Usuario admin no encontrado")
            return False
        
        # Probar contraseña
        test_password = "admin123"
        if verify_password(test_password, admin_user.hashed_password):
            print("✅ Verificación de contraseña exitosa")
            
            # Simular login
            admin_user.last_login = datetime.utcnow()
            db.commit()
            print("✅ Login simulado exitosamente")
            return True
        else:
            print("❌ Verificación de contraseña fallida")
            return False
            
    except Exception as e:
        print(f"❌ Error probando login: {e}")
        return False
    finally:
        db.close()

def show_admin_info():
    """Mostrar información del usuario admin"""
    print("\n👤 Información del usuario admin:")
    
    db = next(get_db())
    
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if admin_user:
            print(f"   ID: {admin_user.id}")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Rol: {admin_user.role}")
            print(f"   Activo: {admin_user.is_active}")
            print(f"   Verificado: {admin_user.is_verified}")
            print(f"   Creado: {admin_user.created_at}")
            print(f"   Actualizado: {admin_user.updated_at}")
            print(f"   Último login: {admin_user.last_login}")
        else:
            print("❌ Usuario admin no encontrado")
            
    except Exception as e:
        print(f"❌ Error obteniendo información: {e}")
    finally:
        db.close()

def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 RESETEO DE CONTRASEÑA ADMIN - SISTEMA POS")
    print("=" * 60)
    print(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Mostrar información actual del admin
    show_admin_info()
    
    # Resetear contraseña
    if reset_admin_password():
        # Probar login
        if test_admin_login():
            print("\n✅ Reseteo completado exitosamente")
            print("\n🔑 Credenciales actualizadas:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("   Endpoint: POST /api/v1/auth/login")
            print("\n📝 Nota: Usa form-data con username y password")
            print("\n🚀 Ya puedes hacer login en la aplicación")
        else:
            print("\n❌ Error probando el login después del reseteo")
    else:
        print("\n❌ Error reseteando la contraseña")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
