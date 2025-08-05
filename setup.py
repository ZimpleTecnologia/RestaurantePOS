#!/usr/bin/env python3
"""
Script de configuración inicial del Sistema POS
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

def create_env_file():
    """Crear archivo .env si no existe"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creando archivo .env...")
        env_content = """# Database Configuration
DATABASE_URL=postgresql://sistema_pos_user:tu_password@localhost:5432/sistema_pos
DATABASE_TEST_URL=postgresql://sistema_pos_user:tu_password@localhost:5432/sistema_pos_test

# Security
SECRET_KEY=tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000

# File Upload Settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Email Settings (for future use)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env creado")
        print("⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones antes de continuar")
        return False
    return True

def install_dependencies():
    """Instalar dependencias"""
    return run_command("pip install -r requirements.txt", "Instalando dependencias")

def create_directories():
    """Crear directorios necesarios"""
    directories = ["uploads", "static", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directorios creados")

def init_database():
    """Inicializar base de datos"""
    print("🗄️  Inicializando base de datos...")
    try:
        from app.database import create_tables
        create_tables()
        print("✅ Tablas de base de datos creadas")
        return True
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        print("⚠️  Asegúrate de que PostgreSQL esté ejecutándose y configurado correctamente")
        return False

def create_admin_user():
    """Crear usuario administrador"""
    print("👤 Creando usuario administrador...")
    try:
        from app.database import SessionLocal
        from app.models.user import User
        from app.auth.security import get_password_hash
        
        db = SessionLocal()
        
        # Verificar si ya existe un usuario admin
        existing_admin = db.query(User).filter(User.username == 'admin').first()
        if existing_admin:
            print("✅ Usuario administrador ya existe")
            db.close()
            return True
        
        admin_user = User(
            username='admin',
            email='admin@sistema.com',
            full_name='Administrador del Sistema',
            hashed_password=get_password_hash('admin123'),
            role='admin',
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.close()
        
        print("✅ Usuario administrador creado")
        print("📋 Credenciales:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("⚠️  IMPORTANTE: Cambia la contraseña después del primer inicio de sesión")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Configuración inicial del Sistema POS")
    print("=" * 50)
    
    # Verificar Python
    check_python_version()
    
    # Crear archivo .env
    env_ready = create_env_file()
    if not env_ready:
        print("\n⚠️  Por favor, edita el archivo .env con tus configuraciones y ejecuta este script nuevamente")
        return
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ Error al instalar dependencias")
        return
    
    # Crear directorios
    create_directories()
    
    # Inicializar base de datos
    if not init_database():
        print("❌ Error al inicializar base de datos")
        return
    
    # Crear usuario administrador
    if not create_admin_user():
        print("❌ Error al crear usuario administrador")
        return
    
    print("\n🎉 ¡Configuración completada exitosamente!")
    print("=" * 50)
    print("📋 Próximos pasos:")
    print("1. Ejecuta la aplicación: uvicorn app.main:app --reload")
    print("2. Accede a: http://localhost:8000")
    print("3. Inicia sesión con: admin / admin123")
    print("4. Cambia la contraseña del administrador")
    print("5. Configura tu negocio (categorías, productos, etc.)")
    
    print("\n📚 Documentación:")
    print("- API Docs: http://localhost:8000/docs")
    print("- README: Lee el archivo README.md para más información")

if __name__ == "__main__":
    main() 