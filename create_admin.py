#!/usr/bin/env python3
"""
Script para crear usuario admin en Docker
"""
import sys
import os

# Agregar path de la aplicación
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database import SessionLocal, create_tables
    from app.models.user import User, UserRole
    from app.auth.security import get_password_hash, verify_password
    
    def main():
        print("🔧 Creando usuario administrador...")
        
        # Crear tablas
        create_tables()
        print("✅ Tablas verificadas")
        
        db = SessionLocal()
        
        try:
            # Eliminar admin existente
            existing = db.query(User).filter(User.username == 'admin').first()
            if existing:
                print("🗑️ Eliminando admin existente...")
                db.delete(existing)
                db.commit()
            
            # Crear hash
            password = "admin123"
            hashed_password = get_password_hash(password)
            print(f"🔐 Hash generado: {hashed_password[:30]}...")
            
            # Verificar el hash funciona
            if not verify_password(password, hashed_password):
                print("❌ Error: El hash generado no es válido")
                return False
            
            print("✅ Hash verificado correctamente")
            
            # Crear usuario
            admin_user = User(
                username='admin',
                email='admin@sistema.com',
                full_name='Administrador del Sistema',
                hashed_password=hashed_password,
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print("✅ Usuario admin creado exitosamente")
            print(f"   ID: {admin_user.id}")
            print(f"   Usuario: admin")
            print(f"   Contraseña: {password}")
            print(f"   Email: {admin_user.email}")
            print(f"   Rol: {admin_user.role}")
            
            # Verificar login
            test_user = db.query(User).filter(User.username == 'admin').first()
            if test_user and verify_password(password, test_user.hashed_password):
                print("✅ Verificación de login: OK")
                return True
            else:
                print("❌ Verificación de login: FALLO")
                return False
                
        finally:
            db.close()
    
    if __name__ == "__main__":
        success = main()
        sys.exit(0 if success else 1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
