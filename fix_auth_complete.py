#!/usr/bin/env python3
"""
Script de corrección completa de autenticación
Uso: python fix_auth_complete.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Configurar contexto de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_database_url():
    """Obtener URL de base de datos desde variables de entorno"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://sistema_pos_user:password@localhost:5432/restaurante_pos"
    )

def fix_authentication():
    """Corrección completa de autenticación"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        print(f"🔗 Conectando a: {database_url.split('@')[1] if '@' in database_url else 'base de datos local'}")
        
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 1. Eliminar usuario admin existente
        print("🗑️  Eliminando usuario admin existente...")
        session.execute(text("DELETE FROM users WHERE username = 'admin'"))
        session.commit()
        
        # 2. Crear usuario admin nuevo
        print("👤 Creando usuario admin nuevo...")
        password = "123456"
        hashed_password = pwd_context.hash(password)
        
        session.execute(text("""
            INSERT INTO users (
                username, 
                email, 
                hashed_password, 
                full_name, 
                is_active, 
                is_admin, 
                is_verified,
                role,
                created_at, 
                updated_at
            ) VALUES (
                :username, 
                :email, 
                :hashed_password, 
                :full_name, 
                :is_active, 
                :is_admin, 
                :is_verified,
                :role,
                CURRENT_TIMESTAMP, 
                CURRENT_TIMESTAMP
            )
        """), {
            "username": "admin",
            "email": "admin@sistema-pos.com",
            "hashed_password": hashed_password,
            "full_name": "Administrador",
            "is_active": True,
            "is_admin": True,
            "is_verified": True,
            "role": "ADMIN"
        })
        
        session.commit()
        
        # 3. Verificar creación
        print("🔍 Verificando usuario creado...")
        result = session.execute(text("""
            SELECT username, is_active, is_admin, is_verified, role 
            FROM users WHERE username = 'admin'
        """))
        admin_user = result.fetchone()
        
        if admin_user:
            username, is_active, is_admin, is_verified, role = admin_user
            print(f"✅ Usuario creado:")
            print(f"   Username: {username}")
            print(f"   Is Active: {is_active}")
            print(f"   Is Admin: {is_admin}")
            print(f"   Is Verified: {is_verified}")
            print(f"   Role: {role}")
        
        # 4. Probar autenticación
        print("🔐 Probando autenticación...")
        if pwd_context.verify(password, hashed_password):
            print("✅ Autenticación funcionando correctamente")
        else:
            print("❌ Error en autenticación")
            return False
        
        print("\n🎉 ¡Corrección completada exitosamente!")
        print("🎯 Credenciales para login:")
        print("   Usuario: admin")
        print("   Contraseña: 123456")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante corrección: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Función principal"""
    print("🔧 Corrección Completa de Autenticación - Sistema POS")
    print("=" * 60)
    
    if fix_authentication():
        print("\n✅ Sistema de autenticación corregido exitosamente")
    else:
        print("\n❌ Error durante la corrección")
        sys.exit(1)

if __name__ == "__main__":
    main()


