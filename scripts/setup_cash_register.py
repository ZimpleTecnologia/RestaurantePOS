#!/usr/bin/env python3
"""
Script para configurar el módulo de caja desde cero
"""
import sys
import os
from decimal import Decimal

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models.settings import SystemSettings
from app.services.cash_service import CashService
from app.models.user import User

def setup_cash_register():
    """Configurar el módulo de caja desde cero"""
    print("🔧 Configurando módulo de caja...")
    
    db = next(get_db())
    
    try:
        # 1. Crear configuración de contraseña de caja
        print("\n1️⃣ Configurando contraseña de caja...")
        
        # Verificar si ya existe
        existing_password = db.query(SystemSettings).filter(
            SystemSettings.setting_key == "cash_register_password"
        ).first()
        
        if not existing_password:
            password_setting = SystemSettings(
                setting_key="cash_register_password",
                setting_value="1234",
                description="Contraseña para acceso al módulo de caja"
            )
            db.add(password_setting)
            print("✅ Contraseña de caja configurada: 1234")
        else:
            print(f"✅ Contraseña de caja ya existe: {existing_password.setting_value}")
        
        # 2. Crear configuración de nombre de caja
        print("\n2️⃣ Configurando nombre de caja...")
        existing_name = db.query(SystemSettings).filter(
            SystemSettings.setting_key == "cash_register_name"
        ).first()
        
        if not existing_name:
            name_setting = SystemSettings(
                setting_key="cash_register_name",
                setting_value="Caja Principal",
                description="Nombre de la caja registradora"
            )
            db.add(name_setting)
            print("✅ Nombre de caja configurado: Caja Principal")
        else:
            print(f"✅ Nombre de caja ya existe: {existing_name.setting_value}")
        
        # 3. Crear configuración de requerir caja para ventas
        print("\n3️⃣ Configurando requerimiento de caja...")
        existing_require = db.query(SystemSettings).filter(
            SystemSettings.setting_key == "require_cash_register"
        ).first()
        
        if not existing_require:
            require_setting = SystemSettings(
                setting_key="require_cash_register",
                setting_value="true",
                description="Requiere caja abierta para ventas"
            )
            db.add(require_setting)
            print("✅ Requerimiento de caja configurado: true")
        else:
            print(f"✅ Requerimiento de caja ya existe: {existing_require.setting_value}")
        
        # 4. Crear caja principal
        print("\n4️⃣ Creando caja principal...")
        cash_register = CashService.get_main_cash_register(db)
        if not cash_register:
            cash_register = CashService.create_main_cash_register(db)
            print(f"✅ Caja principal creada: {cash_register.name}")
        else:
            print(f"✅ Caja principal ya existe: {cash_register.name}")
        
        # 5. Verificar usuarios
        print("\n5️⃣ Verificando usuarios...")
        users = db.query(User).all()
        if users:
            print(f"✅ Usuarios encontrados: {len(users)}")
            for user in users:
                print(f"   - {user.full_name} ({user.username})")
        else:
            print("⚠️ No hay usuarios en el sistema")
        
        db.commit()
        
        print("\n✅ Configuración del módulo de caja completada")
        
        # 6. Mostrar resumen
        print("\n📋 RESUMEN DE CONFIGURACIÓN:")
        print("   🔑 Contraseña de caja: 1234")
        print("   🏦 Nombre de caja: Caja Principal")
        print("   🔒 Requiere caja para ventas: Sí")
        print("   👥 Usuarios disponibles: " + str(len(users)))
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando módulo de caja: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

def test_cash_register():
    """Probar el módulo de caja configurado"""
    print("\n🧪 Probando módulo de caja...")
    
    db = next(get_db())
    
    try:
        # 1. Verificar contraseña
        password_setting = db.query(SystemSettings).filter(
            SystemSettings.setting_key == "cash_register_password"
        ).first()
        
        if password_setting and password_setting.setting_value == "1234":
            print("✅ Contraseña verificada correctamente")
        else:
            print("❌ Error en contraseña")
            return False
        
        # 2. Verificar caja
        cash_register = CashService.get_main_cash_register(db)
        if cash_register:
            print(f"✅ Caja principal verificada: {cash_register.name}")
        else:
            print("❌ Error en caja principal")
            return False
        
        # 3. Verificar restricción de ventas
        require_setting = db.query(SystemSettings).filter(
            SystemSettings.setting_key == "require_cash_register"
        ).first()
        
        if require_setting and require_setting.setting_value == "true":
            print("✅ Restricción de ventas verificada")
        else:
            print("❌ Error en restricción de ventas")
            return False
        
        print("✅ Todas las verificaciones pasaron")
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 70)
    print("🔧 CONFIGURACIÓN DEL MÓDULO UNIFICADO DE CAJA")
    print("=" * 70)
    
    # Configurar módulo
    if setup_cash_register():
        # Probar módulo
        test_cash_register()
    
    print("\n" + "=" * 70)
    print("✅ Configuración completada")

if __name__ == "__main__":
    main()
