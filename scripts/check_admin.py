#!/usr/bin/env python3
"""
Script para verificar el estado del usuario admin y diagnosticar problemas de autenticación
"""
import sys
import os
import time
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, create_tables
from app.models.user import User, UserRole
from app.auth.security import get_password_hash, verify_password
from app.config import settings

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print("🔄 Verificando conexión a la base de datos...")
    
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Conexión a la base de datos establecida")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def check_admin_user():
    """Verificar si existe el usuario admin"""
    print("\n👤 Verificando usuario administrador...")
    
    db = next(get_db())
    
    try:
        # Buscar usuario admin
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if admin_user:
            print("✅ Usuario admin encontrado:")
            print(f"   ID: {admin_user.id}")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Rol: {admin_user.role}")
            print(f"   Activo: {admin_user.is_active}")
            print(f"   Verificado: {admin_user.is_verified}")
            print(f"   Creado: {admin_user.created_at}")
            print(f"   Último login: {admin_user.last_login}")
            
            # Verificar contraseña
            test_password = "admin123"
            if verify_password(test_password, admin_user.hashed_password):
                print("✅ Contraseña correcta")
                return admin_user
            else:
                print("❌ Contraseña incorrecta")
                return None
        else:
            print("❌ Usuario admin no encontrado")
            return None
            
    except Exception as e:
        print(f"❌ Error verificando admin: {e}")
        return None
    finally:
        db.close()

def create_admin_user():
    """Crear usuario admin si no existe"""
    print("\n🔧 Creando usuario administrador...")
    
    db = next(get_db())
    
    try:
        # Verificar si ya existe
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✅ Usuario admin ya existe")
            return existing_admin
        
        # Crear hash de contraseña
        password = "admin123"
        hashed_password = get_password_hash(password)
        
        # Crear usuario admin
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
        print(f"   Usuario: {admin_user.username}")
        print(f"   Contraseña: {password}")
        print(f"   Email: {admin_user.email}")
        print(f"   Rol: {admin_user.role}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creando admin: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def test_login():
    """Probar el proceso de login"""
    print("\n🔐 Probando proceso de login...")
    
    db = next(get_db())
    
    try:
        # Buscar usuario admin
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            print("❌ No se puede probar login: usuario admin no existe")
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

def check_all_users():
    """Verificar todos los usuarios en la base de datos"""
    print("\n👥 Verificando todos los usuarios...")
    
    db = next(get_db())
    
    try:
        users = db.query(User).all()
        
        if users:
            print(f"📊 Total de usuarios: {len(users)}")
            for user in users:
                print(f"   - {user.username} ({user.email}) - Rol: {user.role} - Activo: {user.is_active}")
        else:
            print("❌ No hay usuarios en la base de datos")
            
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")
    finally:
        db.close()

def check_database_tables():
    """Verificar que las tablas existen"""
    print("\n📋 Verificando tablas de la base de datos...")
    
    db = next(get_db())
    
    try:
        # Crear tablas si no existen
        create_tables()
        print("✅ Tablas verificadas/creadas")
        
        # Verificar tabla users específicamente
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"📊 Registros en tabla users: {count}")
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
    finally:
        db.close()

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE AUTENTICACIÓN - SISTEMA POS")
    print("=" * 60)
    print(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar conexión
    if not check_database_connection():
        print("❌ No se puede continuar sin conexión a la base de datos")
        sys.exit(1)
    
    # Verificar tablas
    check_database_tables()
    
    # Verificar todos los usuarios
    check_all_users()
    
    # Verificar usuario admin
    admin_user = check_admin_user()
    
    if not admin_user:
        print("\n⚠️  Usuario admin no encontrado o con problemas")
        print("🔧 Creando nuevo usuario admin...")
        admin_user = create_admin_user()
    
    if admin_user:
        # Probar login
        if test_login():
            print("\n✅ Diagnóstico completado - Sistema listo")
            print("\n🔑 Credenciales para login:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("   Endpoint: POST /api/v1/auth/login")
            print("\n📝 Nota: Usa form-data con username y password")
        else:
            print("\n❌ Problema con el proceso de login")
    else:
        print("\n❌ No se pudo crear/verificar usuario admin")
    
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
