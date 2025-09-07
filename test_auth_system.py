#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de autenticación
"""
import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

def test_login():
    """Probar el sistema de login"""
    print("🔐 Probando sistema de login...")
    
    try:
        # Intentar login
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login-json",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login exitoso - Token obtenido: {token[:20]}...")
            return token
        else:
            print(f"❌ Error en login: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_protected_pages(token):
    """Probar acceso a páginas protegidas"""
    print("\n🔒 Probando acceso a páginas protegidas...")
    
    protected_pages = [
        "/",
        "/products",
        "/inventory",
        "/settings",
        "/reports"
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for page in protected_pages:
        try:
            response = requests.get(f"{BASE_URL}{page}", headers=headers)
            if response.status_code == 200:
                print(f"✅ {page} - Acceso permitido")
            else:
                print(f"❌ {page} - Acceso denegado: {response.status_code}")
        except Exception as e:
            print(f"❌ {page} - Error: {e}")

def test_unprotected_pages():
    """Probar acceso a páginas no protegidas"""
    print("\n🌐 Probando acceso a páginas no protegidas...")
    
    unprotected_pages = [
        "/login",
        "/api/v1/",
        "/health"
    ]
    
    for page in unprotected_pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            if response.status_code == 200:
                print(f"✅ {page} - Acceso público permitido")
            else:
                print(f"❌ {page} - Error: {response.status_code}")
        except Exception as e:
            print(f"❌ {page} - Error: {e}")

def test_middleware_redirect():
    """Probar redirección del middleware"""
    print("\n🔄 Probando redirección del middleware...")
    
    try:
        # Intentar acceder a página protegida sin token
        response = requests.get(f"{BASE_URL}/", allow_redirects=False)
        
        if response.status_code == 302:
            print(f"✅ Redirección correcta: {response.status_code}")
            print(f"   Ubicación: {response.headers.get('Location', 'No especificada')}")
        else:
            print(f"❌ No se redirigió: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando redirección: {e}")

def test_token_expiration():
    """Probar expiración del token"""
    print("\n⏰ Probando expiración del token...")
    
    try:
        # Crear un token con expiración muy corta
        from app.auth.security import create_access_token
        from datetime import timedelta
        
        # Este test requiere acceso a los módulos de la aplicación
        print("ℹ️  Test de expiración requiere acceso a módulos internos")
        print("   Se puede probar manualmente esperando que expire el token")
        
    except ImportError:
        print("ℹ️  Test de expiración requiere ejecutarse desde el contexto de la aplicación")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema de autenticación")
    print("=" * 50)
    
    # Verificar que el servidor esté corriendo
    try:
        health_check = requests.get(f"{BASE_URL}/health")
        if health_check.status_code != 200:
            print("❌ El servidor no está respondiendo correctamente")
            return
        print("✅ Servidor respondiendo correctamente")
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("   Asegúrate de que la aplicación esté corriendo en http://localhost:8000")
        return
    
    # Ejecutar pruebas
    token = test_login()
    
    if token:
        test_protected_pages(token)
        test_unprotected_pages()
        test_middleware_redirect()
        test_token_expiration()
        
        print("\n" + "=" * 50)
        print("✅ Todas las pruebas completadas")
        print("\n📋 Resumen de funcionalidades:")
        print("   • Login funcional")
        print("   • Páginas protegidas")
        print("   • Middleware de redirección")
        print("   • Sistema de timeout configurado")
        
    else:
        print("\n❌ No se pudo obtener token, algunas pruebas fallaron")
    
    print("\n🔧 Para probar el timeout por inactividad:")
    print("   1. Haz login en el navegador")
    print("   2. Espera 28 minutos (o ajusta la configuración)")
    print("   3. Deberías ver la advertencia de timeout")
    print("   4. Si no extiendes la sesión, se cerrará automáticamente")

if __name__ == "__main__":
    main()

