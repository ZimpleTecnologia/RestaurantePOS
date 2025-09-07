#!/usr/bin/env python3
"""
Script simple para probar que la aplicación se pueda importar sin errores
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Probar que todos los módulos se puedan importar"""
    print("🧪 Probando importaciones...")
    
    try:
        print("  📦 Importando app.config...")
        from app.config import settings
        print(f"    ✅ Configuración cargada - Puerto: {settings.port}")
        
        print("  📦 Importando app.middleware...")
        from app.middleware import AuthMiddleware, SessionTimeoutMiddleware
        print("    ✅ Middlewares importados correctamente")
        
        print("  📦 Importando app.main...")
        from app.main import app
        print("    ✅ Aplicación FastAPI importada correctamente")
        
        print("\n🎉 ¡Todas las importaciones exitosas!")
        print("   La aplicación debería iniciar correctamente ahora.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en importación: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False

def test_config():
    """Probar la configuración"""
    print("\n⚙️  Probando configuración...")
    
    try:
        from app.config import settings
        
        print(f"  🔐 Secret Key: {'Configurado' if settings.secret_key != 'your-secret-key-here-change-in-production' else 'Por defecto'}")
        print(f"  ⏰ Token Expire: {settings.access_token_expire_minutes} minutos")
        print(f"  🕐 Session Timeout: {settings.session_timeout_minutes} minutos")
        print(f"  🌐 Host: {settings.host}")
        print(f"  🚪 Puerto: {settings.port}")
        print(f"  🐛 Debug: {settings.debug}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en configuración: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de importación")
    print("=" * 50)
    
    # Probar importaciones
    imports_ok = test_imports()
    
    if imports_ok:
        # Probar configuración
        config_ok = test_config()
        
        if config_ok:
            print("\n✅ TODAS LAS PRUEBAS EXITOSAS")
            print("\n🎯 Ahora puedes iniciar la aplicación con:")
            print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        else:
            print("\n⚠️  Importaciones OK pero problemas de configuración")
    else:
        print("\n❌ PROBLEMAS DE IMPORTACIÓN")
        print("\n🔍 Revisar:")
        print("   • Que todos los archivos estén en su lugar")
        print("   • Que no haya errores de sintaxis")
        print("   • Que las dependencias estén instaladas")

if __name__ == "__main__":
    main()

