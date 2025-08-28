#!/usr/bin/env python3
"""
Script para probar el endpoint de apertura de caja
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ABRIR_CAJA_URL = f"{BASE_URL}/api/v1/caja-ventas/abrir-caja"

def test_abrir_caja():
    """Probar el endpoint de apertura de caja"""
    print("=" * 60)
    print("🧪 PRUEBA DE APERTURA DE CAJA")
    print("=" * 60)
    
    # 1. Hacer login para obtener token
    print("\n1️⃣ Haciendo login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, data=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login exitoso! Token: {token[:20]}...")
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # 2. Probar apertura de caja
    print("\n2️⃣ Probando apertura de caja...")
    apertura_data = {
        "password": "1234",  # Contraseña por defecto
        "fondo_inicial": 50000.00,
        "notas_apertura": "Prueba de apertura desde script"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(ABRIR_CAJA_URL, json=apertura_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Caja abierta exitosamente!")
            print(f"   - Sesión: {data.get('sesion', {}).get('session_number')}")
            print(f"   - Fondo inicial: ${data.get('sesion', {}).get('fondo_inicial')}")
            print(f"   - Usuario: {data.get('sesion', {}).get('user_name')}")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   - Detalle: {error_data.get('detail')}")
            except:
                print(f"   - Respuesta: {response.text}")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada")

if __name__ == "__main__":
    test_abrir_caja()
