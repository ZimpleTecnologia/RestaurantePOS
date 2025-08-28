#!/usr/bin/env python3
"""
Script para configurar la contraseña de caja
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.services.settings_service import SettingsService

def configurar_caja():
    """Configurar la contraseña de caja"""
    print("=" * 60)
    print("🔧 CONFIGURACIÓN DE CAJA")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. Verificar contraseña actual
        print("\n1️⃣ Verificando contraseña actual...")
        current_password = SettingsService.get_cash_register_password(db)
        print(f"   Contraseña actual: '{current_password}'")
        
        # 2. Configurar nueva contraseña
        print("\n2️⃣ Configurando nueva contraseña...")
        new_password = "1234"  # Contraseña estándar
        
        SettingsService.set_cash_register_password(db, new_password)
        print(f"   ✅ Contraseña configurada: '{new_password}'")
        
        # 3. Verificar que se guardó correctamente
        print("\n3️⃣ Verificando configuración...")
        stored_password = SettingsService.get_cash_register_password(db)
        print(f"   Contraseña almacenada: '{stored_password}'")
        
        if stored_password == new_password:
            print("   ✅ Contraseña configurada correctamente!")
        else:
            print("   ❌ Error: La contraseña no se guardó correctamente")
            
        # 4. Verificar otras configuraciones
        print("\n4️⃣ Verificando otras configuraciones...")
        require_cash_register = SettingsService.get_setting(db, "require_cash_register", "true")
        print(f"   Requiere caja: {require_cash_register}")
        
        # 5. Inicializar configuraciones por defecto si es necesario
        print("\n5️⃣ Inicializando configuraciones por defecto...")
        SettingsService.initialize_default_settings(db)
        print("   ✅ Configuraciones inicializadas")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("✅ Configuración completada")

if __name__ == "__main__":
    configurar_caja()
