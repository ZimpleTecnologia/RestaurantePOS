#!/usr/bin/env python3
"""
Script de prueba simplificado para verificar el sistema de autenticación
"""
import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

def test_server_health():
    """Probar que el servidor esté respondiendo"""
    print("🏥 Probando salud del servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor respondiendo correctamente")
            return True
        else:
            print(f"❌ Servidor no responde correctamente: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return False

def test_login():
    """Probar el sistema de login"""
    print("\n🔐 Probando sistema de login...")
    
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

def test_middleware_redirect():
    """Probar redirección del middleware"""
    print("\n🔄 Probando redirección del middleware...")
    
    try:
        # Intentar acceder a página protegida sin token
        response = requests.get(f"{BASE_URL}/", allow_redirects=False)
        
        if response.status_code == 302:
            print(f"✅ Redirección correcta: {response.status_code}")
            print(f"   Ubicación: {response.headers.get('Location', 'No especificada')}")
            return True
        else:
            print(f"❌ No se redirigió: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando redirección: {e}")
        return False

def test_protected_pages_without_token():
    """Probar acceso a páginas protegidas sin token"""
    print("\n🔒 Probando acceso a páginas protegidas sin token...")
    
    protected_pages = [
        "/",
        "/products",
        "/inventory",
        "/settings",
        "/reports"
    ]
    
    all_redirected = True
    
    for page in protected_pages:
        try:
            response = requests.get(f"{BASE_URL}{page}", allow_redirects=False)
            if response.status_code == 302:
                print(f"✅ {page} - Redirección correcta a login")
            else:
                print(f"❌ {page} - No se redirigió: {response.status_code}")
                all_redirected = False
        except Exception as e:
            print(f"❌ {page} - Error: {e}")
            all_redirected = False
    
    return all_redirected

def test_unprotected_pages():
    """Probar acceso a páginas no protegidas"""
    print("\n🌐 Probando acceso a páginas no protegidas...")
    
    unprotected_pages = [
        "/login",
        "/api/v1/",
        "/health"
    ]
    
    all_accessible = True
    
    for page in unprotected_pages:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            if response.status_code == 200:
                print(f"✅ {page} - Acceso público permitido")
            else:
                print(f"❌ {page} - Error: {response.status_code}")
                all_accessible = False
        except Exception as e:
            print(f"❌ {page} - Error: {e}")
            all_accessible = False
    
    return all_accessible

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema de autenticación")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    if not test_server_health():
        print("\n❌ El servidor no está respondiendo correctamente")
        print("   Asegúrate de que la aplicación esté corriendo en http://localhost:8000")
        return
    
    # Ejecutar pruebas
    print("\n" + "=" * 60)
    print("🔍 EJECUTANDO PRUEBAS DEL MIDDLEWARE")
    print("=" * 60)
    
    # Probar redirección del middleware
    middleware_ok = test_middleware_redirect()
    
    # Probar páginas protegidas sin token
    protected_ok = test_protected_pages_without_token()
    
    # Probar páginas no protegidas
    unprotected_ok = test_unprotected_pages()
    
    # Probar login (opcional)
    print("\n" + "=" * 60)
    print("🔐 PRUEBAS DE LOGIN (OPCIONAL)")
    print("=" * 60)
    
    token = test_login()
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    if middleware_ok and protected_ok and unprotected_ok:
        print("✅ TODAS LAS PRUEBAS DEL MIDDLEWARE EXITOSAS")
        print("\n🎯 El sistema de autenticación está funcionando correctamente:")
        print("   • Las páginas protegidas redirigen al login")
        print("   • Las páginas públicas son accesibles")
        print("   • El middleware está activo")
        
        if token:
            print("\n🔑 Login funcional - Token obtenido correctamente")
        else:
            print("\n⚠️  Login no funcional - Verificar credenciales o endpoint")
            
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("\n🔍 Revisar:")
        if not middleware_ok:
            print("   • Middleware de autenticación")
        if not protected_ok:
            print("   • Protección de páginas")
        if not unprotected_ok:
            print("   • Acceso a páginas públicas")
    
    print("\n" + "=" * 60)
    print("🔧 PRÓXIMOS PASOS")
    print("=" * 60)
    print("1. Si las pruebas del middleware fallaron:")
    print("   • Verificar que app/middleware.py esté correcto")
    print("   • Comprobar que app/main.py incluya los middlewares")
    print("   • Revisar la consola del servidor para errores")
    
    print("\n2. Para probar el timeout por inactividad:")
    print("   • Haz login en el navegador")
    print("   • Espera 28 minutos (o ajusta la configuración)")
    print("   • Deberías ver la advertencia de timeout")
    
    print("\n3. Para verificar el frontend:")
    print("   • Abre la consola del navegador")
    print("   • Deberías ver: 'Sistema de autenticación inicializado'")
    print("   • Si no aparece, verificar que /static/js/auth.js se cargue")

if __name__ == "__main__":
    main()

