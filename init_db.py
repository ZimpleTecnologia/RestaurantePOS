#!/usr/bin/env python3
"""
Script de inicialización de la base de datos
Se ejecuta automáticamente al iniciar el contenedor
"""
import sys
import os
import time

# Configurar variables de entorno para Docker
os.environ["DATABASE_URL"] = "postgresql://sistema_pos_user:sistema_pos_password@postgres:5432/sistema_pos"
os.environ["SECRET_KEY"] = "tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DEBUG"] = "True"

# Agregar path de la aplicación
sys.path.insert(0, '/app')

def wait_for_database():
    """Esperar a que la base de datos esté disponible"""
    print("🔄 Esperando a que la base de datos esté disponible...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            from app.database import engine
from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Base de datos disponible")
            return True
        except Exception as e:
            attempt += 1
            print(f"⏳ Intento {attempt}/{max_attempts}: Base de datos no disponible aún...")
            time.sleep(2)
    
    print("❌ No se pudo conectar a la base de datos después de 60 segundos")
    return False

def init_database():
    """Inicializar la base de datos"""
    try:
        from app.database import SessionLocal, create_tables
        from app.models.user import User, UserRole
        from app.auth.security import get_password_hash, verify_password
        
        print("🔧 Inicializando base de datos...")
        
        # Crear tablas
        create_tables()
        print("✅ Tablas creadas")
        
        db = SessionLocal()
        
        try:
            # Verificar si ya existe un admin
            existing_admin = db.query(User).filter(User.username == 'admin').first()
            if existing_admin:
                print("✅ Usuario admin ya existe")
                return True
            
            # Crear hash
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
            print(f"   Usuario: admin")
            print(f"   Contraseña: {password}")
            
            return True
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando Sistema POS...")
    
    # Esperar a que la base de datos esté disponible
    if not wait_for_database():
        return False
    
    # Inicializar la base de datos
    if not init_database():
        return False
    
    print("✅ Inicialización completada exitosamente")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

