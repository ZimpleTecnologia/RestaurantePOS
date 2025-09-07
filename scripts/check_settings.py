#!/usr/bin/env python3
"""
Script para verificar configuraciones del sistema
"""
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import get_db

def check_settings():
    """Verificar configuraciones del sistema"""
    print("🔍 Verificando configuraciones del sistema...")
    
    db = next(get_db())
    
    try:
        # Verificar si la tabla existe
        result = db.execute(text("SELECT COUNT(*) FROM system_settings"))
        count = result.scalar()
        print(f"📊 Registros en system_settings: {count}")
        
        if count > 0:
            # Obtener todas las configuraciones
            result = db.execute(text("SELECT setting_key, setting_value, description FROM system_settings"))
            rows = result.fetchall()
            
            print("\n📋 Configuraciones existentes:")
            for row in rows:
                print(f"  - {row[0]}: {row[1]} ({row[2]})")
        
        # Verificar si existe la configuración de contraseña de caja
        result = db.execute(text("SELECT setting_value FROM system_settings WHERE setting_key = 'cash_register_password'"))
        password_setting = result.fetchone()
        
        if password_setting:
            print(f"\n🔑 Contraseña de caja: {password_setting[0]}")
        else:
            print("\n⚠️ No existe configuración de contraseña de caja")
        
    except Exception as e:
        print(f"❌ Error verificando configuraciones: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIONES")
    print("=" * 60)
    
    check_settings()
    
    print("\n" + "=" * 60)
    print("✅ Verificación completada")

if __name__ == "__main__":
    main()
