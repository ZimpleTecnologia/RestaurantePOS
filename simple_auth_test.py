#!/usr/bin/env python3
"""
Script simple para probar autenticación
Uso: python simple_auth_test.py
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

def simple_test():
    """Prueba simple de autenticación"""
    try:
        print("🔍 Prueba Simple de Autenticación")
        print("=" * 40)
        
        # 1. Probar bcrypt localmente
        print("1️⃣ Probando bcrypt localmente...")
        test_password = "123456"
        test_hash = pwd_context.hash(test_password)
        print(f"   Contraseña: {test_password}")
        print(f"   Hash generado: {test_hash}")
        
        if pwd_context.verify(test_password, test_hash):
            print("   ✅ bcrypt funciona correctamente")
        else:
            print("   ❌ bcrypt NO funciona")
            return False
        
        # 2. Conectar a la base de datos
        print("\n2️⃣ Conectando a la base de datos...")
        database_url = get_database_url()
        print(f"   URL: {database_url.split('@')[1] if '@' in database_url else 'local'}")
        
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 3. Obtener usuario admin
        print("\n3️⃣ Obteniendo usuario admin...")
        result = session.execute(text("SELECT username, hashed_password FROM users WHERE username = 'admin'"))
        admin_user = result.fetchone()
        
        if not admin_user:
            print("   ❌ Usuario admin no encontrado")
            return False
        
        username, db_hash = admin_user
        print(f"   Usuario: {username}")
        print(f"   Hash en BD: {db_hash[:50]}...")
        
        # 4. Probar verificación
        print("\n4️⃣ Probando verificación...")
        if pwd_context.verify(test_password, db_hash):
            print("   ✅ Contraseña '123456' es VÁLIDA")
            return True
        else:
            print("   ❌ Contraseña '123456' es INVÁLIDA")
            
            # 5. Generar nuevo hash y actualizar
            print("\n5️⃣ Generando nuevo hash...")
            new_hash = pwd_context.hash("123456")
            print(f"   Nuevo hash: {new_hash}")
            
            session.execute(text("""
                UPDATE users 
                SET hashed_password = :password, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE username = 'admin'
            """), {"password": new_hash})
            session.commit()
            
            # 6. Verificar nuevo hash
            print("\n6️⃣ Verificando nuevo hash...")
            if pwd_context.verify("123456", new_hash):
                print("   ✅ Nuevo hash verificado correctamente")
                return True
            else:
                print("   ❌ Error con el nuevo hash")
                return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Función principal"""
    if simple_test():
        print("\n🎉 ¡Autenticación funcionando!")
        print("🎯 Intenta hacer login con:")
        print("   Usuario: admin")
        print("   Contraseña: 123456")
    else:
        print("\n❌ Problemas con la autenticación")

if __name__ == "__main__":
    main()


