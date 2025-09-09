#!/usr/bin/env python3
"""
Script para probar la autenticación y generar hash correcto
Uso: python test_auth.py
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

def test_authentication():
    """Probar autenticación con diferentes contraseñas"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        print(f"🔗 Conectando a: {database_url.split('@')[1] if '@' in database_url else 'base de datos local'}")
        
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Obtener usuario admin
        result = session.execute(text("SELECT username, hashed_password FROM users WHERE username = 'admin'"))
        admin_user = result.fetchone()
        
        if not admin_user:
            print("❌ Usuario admin no encontrado")
            return False
        
        username, current_hash = admin_user
        print(f"👤 Usuario: {username}")
        print(f"🔐 Hash actual: {current_hash}")
        
        # Probar diferentes contraseñas
        passwords_to_test = [
            "123456",
            "admin123", 
            "admin",
            "password",
            "12345"
        ]
        
        print("\n🔍 Probando contraseñas:")
        print("-" * 50)
        
        for password in passwords_to_test:
            is_valid = pwd_context.verify(password, current_hash)
            status = "✅ VÁLIDA" if is_valid else "❌ Inválida"
            print(f"{password:12} -> {status}")
            
            if is_valid:
                print(f"\n🎉 ¡Contraseña encontrada: '{password}'")
                return True
        
        print("\n⚠️  Ninguna contraseña funcionó. Generando nuevo hash para '123456'...")
        
        # Generar nuevo hash para '123456'
        new_hash = pwd_context.hash("123456")
        print(f"🔐 Nuevo hash para '123456': {new_hash}")
        
        # Actualizar en la base de datos
        session.execute(text("""
            UPDATE users 
            SET hashed_password = :password, 
                updated_at = CURRENT_TIMESTAMP
            WHERE username = 'admin'
        """), {"password": new_hash})
        
        session.commit()
        
        # Verificar que funciona
        if pwd_context.verify("123456", new_hash):
            print("✅ Hash actualizado y verificado correctamente")
            print("\n🎯 Ahora puedes hacer login con:")
            print("   Usuario: admin")
            print("   Contraseña: 123456")
            return True
        else:
            print("❌ Error actualizando el hash")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Función principal"""
    print("🔐 Prueba de Autenticación - Sistema POS")
    print("=" * 50)
    
    if test_authentication():
        print("\n✅ Autenticación configurada correctamente")
    else:
        print("\n❌ Error configurando autenticación")
        sys.exit(1)

if __name__ == "__main__":
    main()

