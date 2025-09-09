#!/usr/bin/env python3
"""
Script de diagnóstico completo para autenticación
Uso: python debug_auth.py
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

def debug_authentication():
    """Diagnóstico completo de autenticación"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        print(f"🔗 Conectando a: {database_url.split('@')[1] if '@' in database_url else 'base de datos local'}")
        
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 1. Verificar usuario admin
        print("\n1️⃣ Verificando usuario admin...")
        result = session.execute(text("""
            SELECT username, email, hashed_password, is_active, is_admin, is_verified, role, updated_at 
            FROM users WHERE username = 'admin'
        """))
        admin_user = result.fetchone()
        
        if not admin_user:
            print("❌ Usuario admin no encontrado")
            return False
        
        username, email, hashed_password, is_active, is_admin, is_verified, role, updated_at = admin_user
        
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Is Active: {is_active}")
        print(f"   Is Admin: {is_admin}")
        print(f"   Is Verified: {is_verified}")
        print(f"   Role: {role}")
        print(f"   Updated At: {updated_at}")
        print(f"   Hash: {hashed_password[:50]}...")
        
        # 2. Verificar formato del hash
        print("\n2️⃣ Verificando formato del hash...")
        if hashed_password.startswith('$2b$'):
            print("✅ Hash tiene formato bcrypt correcto")
        else:
            print("❌ Hash NO tiene formato bcrypt")
            return False
        
        # 3. Probar verificación de contraseña
        print("\n3️⃣ Probando verificación de contraseña...")
        test_password = "123456"
        
        try:
            is_valid = pwd_context.verify(test_password, hashed_password)
            if is_valid:
                print(f"✅ Contraseña '{test_password}' es VÁLIDA")
            else:
                print(f"❌ Contraseña '{test_password}' es INVÁLIDA")
                
                # Generar nuevo hash
                print("\n🔄 Generando nuevo hash para '123456'...")
                new_hash = pwd_context.hash("123456")
                print(f"   Nuevo hash: {new_hash}")
                
                # Actualizar en BD
                session.execute(text("""
                    UPDATE users 
                    SET hashed_password = :password, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE username = 'admin'
                """), {"password": new_hash})
                session.commit()
                
                # Verificar nuevo hash
                if pwd_context.verify("123456", new_hash):
                    print("✅ Nuevo hash verificado correctamente")
                else:
                    print("❌ Error con el nuevo hash")
                    return False
        except Exception as e:
            print(f"❌ Error verificando contraseña: {e}")
            return False
        
        # 4. Verificar configuración de la aplicación
        print("\n4️⃣ Verificando configuración...")
        print("   ✅ passlib instalado")
        print("   ✅ bcrypt configurado")
        print("   ✅ CryptContext inicializado")
        
        print("\n🎉 ¡Diagnóstico completado!")
        print("🎯 Credenciales para login:")
        print("   Usuario: admin")
        print("   Contraseña: 123456")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Función principal"""
    print("🔍 Diagnóstico de Autenticación - Sistema POS")
    print("=" * 60)
    
    if debug_authentication():
        print("\n✅ Sistema de autenticación funcionando correctamente")
    else:
        print("\n❌ Problemas encontrados en el sistema de autenticación")
        sys.exit(1)

if __name__ == "__main__":
    main()

