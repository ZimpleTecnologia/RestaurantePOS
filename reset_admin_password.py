#!/usr/bin/env python3
"""
Script para resetear la contraseña del usuario administrador
Uso: python reset_admin_password.py
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

def reset_admin_password():
    """Resetear contraseña del usuario admin"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        print(f"🔗 Conectando a: {database_url.split('@')[1] if '@' in database_url else 'base de datos local'}")
        
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar si existe el usuario admin
        result = session.execute(text("SELECT id, username, email FROM users WHERE username = 'admin'"))
        admin_user = result.fetchone()
        
        if not admin_user:
            print("❌ Usuario 'admin' no encontrado")
            print("🔍 Usuarios disponibles:")
            result = session.execute(text("SELECT id, username, email, is_active FROM users"))
            users = result.fetchall()
            for user in users:
                print(f"   - ID: {user[0]}, Usuario: {user[1]}, Email: {user[2]}, Activo: {user[3]}")
            return False
        
        print(f"✅ Usuario admin encontrado: {admin_user[1]} ({admin_user[2]})")
        
        # Generar nueva contraseña
        new_password = "admin123"
        hashed_password = pwd_context.hash(new_password)
        
        # Actualizar contraseña
        session.execute(text("""
            UPDATE users 
            SET hashed_password = :password, 
                is_active = true,
                updated_at = CURRENT_TIMESTAMP
            WHERE username = 'admin'
        """), {"password": hashed_password})
        
        session.commit()
        
        print("🎉 ¡Contraseña resetada exitosamente!")
        print(f"👤 Usuario: admin")
        print(f"🔑 Contraseña: {new_password}")
        print("⚠️  IMPORTANTE: Cambia esta contraseña después del primer login")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def create_admin_user():
    """Crear usuario admin si no existe"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar si existe el usuario admin
        result = session.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        if result.fetchone():
            print("✅ Usuario admin ya existe")
            return True
        
        # Crear usuario admin
        password = "admin123"
        hashed_password = pwd_context.hash(password)
        
        session.execute(text("""
            INSERT INTO users (username, email, hashed_password, full_name, is_active, is_admin, created_at, updated_at)
            VALUES ('admin', 'admin@restaurante.com', :password, 'Administrador', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """), {"password": hashed_password})
        
        session.commit()
        
        print("🎉 ¡Usuario admin creado exitosamente!")
        print(f"👤 Usuario: admin")
        print(f"🔑 Contraseña: {password}")
        print("⚠️  IMPORTANTE: Cambia esta contraseña después del primer login")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Función principal"""
    print("🔐 Reset de Credenciales - Sistema POS")
    print("=" * 50)
    
    # Intentar resetear contraseña
    if reset_admin_password():
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n🔄 Intentando crear usuario admin...")
        if create_admin_user():
            print("\n✅ Usuario admin creado exitosamente")
        else:
            print("\n❌ No se pudo crear/resetear el usuario admin")
            sys.exit(1)

if __name__ == "__main__":
    main()
