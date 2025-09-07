#!/usr/bin/env python3
"""
Script para probar el sistema de login
"""
import sys
import os
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ME_URL = f"{BASE_URL}/api/v1/auth/me"

def test_login():
    """Probar el sistema de login"""
    print("=" * 60)
    print("🧪 PRUEBAS DEL SISTEMA DE LOGIN")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print("✅ Servidor detectado en http://localhost:8000")
    except:
        print("❌ No se puede conectar al servidor en http://localhost:8000")
        print("   Asegúrate de que el servidor esté corriendo con: uvicorn app.main:app --reload")
        return
    
    # 1. Probar login con credenciales correctas
    print("\n1️⃣ Probando login con credenciales correctas...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, data=login_data)
        print(f"Status: {response.status_code}")
        
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
            
            me_response = requests.get(ME_URL, headers=headers)
            print(f"Status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ Usuario autenticado:")
                print(f"   - Usuario: {user_data.get('username')}")
                print(f"   - Email: {user_data.get('email')}")
                print(f"   - Activo: {user_data.get('is_active')}")
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
        response = requests.post(LOGIN_URL, data=wrong_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctamente rechazado con credenciales incorrectas")
        else:
            print(f"❌ Comportamiento inesperado: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 4. Probar endpoint /me sin token
    print("\n4️⃣ Probando endpoint /me sin token...")
    try:
        response = requests.get(ME_URL)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctamente rechazado sin token")
        else:
            print(f"❌ Comportamiento inesperado: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas del sistema de login completadas")

if __name__ == "__main__":
    test_login()
