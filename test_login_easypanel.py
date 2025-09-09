#!/usr/bin/env python3
"""
Script para probar el sistema de login en EasyPanel
"""
import sys
import os
import requests
import json

# Configuración para EasyPanel
BASE_URL = "http://localhost:8000"  # Cambiar si es necesario
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login-json"  # Usar el endpoint correcto
ME_URL = f"{BASE_URL}/api/v1/auth/me"

def test_login():
    """Probar el sistema de login"""
    print("=" * 60)
    print("🧪 PRUEBAS DEL SISTEMA DE LOGIN - EASYPANEL")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ Servidor detectado en http://localhost:8000")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("   Verificando si la aplicación está corriendo...")
        return
    
    # 1. Probar login con credenciales correctas
    print("\n1️⃣ Probando login con credenciales correctas...")
    login_data = {
        "username": "admin",
        "password": "123456"  # Contraseña que configuramos
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login exitoso!")
            print(f"   - Token obtenido: {token[:20]}...")
            print(f"   - Tipo de token: {data.get('token_type')}")
            
            # 2. Probar endpoint /me con el token
            print("\n2️⃣ Probando endpoint /me con el token...")
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            me_response = requests.get(ME_URL, headers=headers, timeout=10)
            print(f"Status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ Usuario autenticado:")
                print(f"   - Usuario: {user_data.get('username')}")
                print(f"   - Email: {user_data.get('email')}")
                print(f"   - Activo: {user_data.get('is_active')}")
                print(f"   - Admin: {user_data.get('is_admin')}")
            else:
                print(f"❌ Error en /me: {me_response.text}")
                
        else:
            print(f"❌ Error en login: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 3. Probar login con credenciales incorrectas
    print("\n3️⃣ Probando login con credenciales incorrectas...")
    wrong_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=wrong_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctamente rechazado con credenciales incorrectas")
        else:
            print(f"❌ Comportamiento inesperado: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 4. Probar diferentes contraseñas
    print("\n4️⃣ Probando diferentes contraseñas...")
    passwords_to_test = ["admin123", "admin", "password", "12345"]
    
    for password in passwords_to_test:
        test_data = {
            "username": "admin",
            "password": password
        }
        
        try:
            response = requests.post(LOGIN_URL, json=test_data, timeout=5)
            status = "✅ VÁLIDA" if response.status_code == 200 else "❌ Inválida"
            print(f"   {password:12} -> {status} (Status: {response.status_code})")
            
            if response.status_code == 200:
                print(f"   🎉 ¡Contraseña encontrada: '{password}'!")
                break
                
        except Exception as e:
            print(f"   {password:12} -> ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas del sistema de login completadas")

if __name__ == "__main__":
    test_login()


