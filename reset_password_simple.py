#!/usr/bin/env python3
"""
Script para resetear la contraseña del admin a una contraseña simple
Uso: python reset_password_simple.py
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

def reset_password_simple():
    """Resetear contraseña a '123456'"""
    try:
        # Conectar a la base de datos
        database_url = get_database_url()
        print(f"🔗 Conectando a: {database_url.split('@')[1] if '@' in database_url else 'base de datos local'}")
        
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Nueva contraseña simple
        new_password = "123456"
        hashed_password = pwd_context.hash(new_password)
        
        # Actualizar contraseña del admin
        result = session.execute(text("""
            UPDATE users 
            SET hashed_password = :password, 
                is_active = true,
                updated_at = CURRENT_TIMESTAMP
            WHERE username = 'admin'
        """), {"password": hashed_password})
        
        session.commit()
        
        if result.rowcount > 0:
            print("🎉 ¡Contraseña resetada exitosamente!")
            print(f"👤 Usuario: admin")
            print(f"🔑 Contraseña: {new_password}")
            print("⚠️  IMPORTANTE: Cambia esta contraseña después del primer login")
            return True
        else:
            print("❌ No se encontró el usuario admin")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Función principal"""
    print("🔐 Reset de Contraseña Simple - Sistema POS")
    print("=" * 50)
    
    if reset_password_simple():
        print("\n✅ Contraseña resetada exitosamente")
        print("🚀 Ahora puedes hacer login con:")
        print("   Usuario: admin")
        print("   Contraseña: 123456")
    else:
        print("\n❌ Error reseteando contraseña")
        sys.exit(1)

if __name__ == "__main__":
    main()
