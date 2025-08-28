#!/usr/bin/env python3
"""
Script para diagnosticar problemas de autenticación
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ESTADO_CAJA_URL = f"{BASE_URL}/api/v1/caja-ventas/estado"
ABRIR_CAJA_URL = f"{BASE_URL}/api/v1/caja-ventas/abrir-caja"

def diagnosticar_auth():
    """Diagnosticar problemas de autenticación"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE AUTENTICACIÓN")
    print("=" * 60)
    
    # 1. Hacer login para obtener token
    print("\n1️⃣ Haciendo login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, data=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"   ✅ Login exitoso!")
            print(f"   Token: {token[:30]}...")
            print(f"   Token type: {data.get('token_type')}")
            print(f"   User: {data.get('user', {}).get('username')}")
        else:
            print(f"   ❌ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return
    
    # 2. Probar endpoint de estado de caja
    print("\n2️⃣ Probando endpoint de estado...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(ESTADO_CAJA_URL, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Estado obtenido!")
            print(f"   Sesión activa: {data.get('sesion_activa')}")
            print(f"   Puede vender: {data.get('puede_vender')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalle: {error_data.get('detail')}")
            except:
                print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 3. Probar apertura de caja
    print("\n3️⃣ Probando apertura de caja...")
    apertura_data = {
        "password": "1234",
        "fondo_inicial": 50000.00,
        "notas_apertura": "Prueba de diagnóstico"
    }
    
    try:
        response = requests.post(ABRIR_CAJA_URL, json=apertura_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Caja abierta exitosamente!")
            print(f"   Sesión: {data.get('sesion', {}).get('session_number')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalle: {error_data.get('detail')}")
            except:
                print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 4. Verificar token en localStorage (simulación)
    print("\n4️⃣ Verificando token en localStorage...")
    print(f"   Token completo: {token}")
    print(f"   Longitud del token: {len(token)}")
    
    # 5. Probar sin token
    print("\n5️⃣ Probando sin token...")
    try:
        response = requests.post(ABRIR_CAJA_URL, json=apertura_data)
        print(f"   Status sin token: {response.status_code}")
        if response.status_code == 401:
            print(f"   ✅ Correcto: Requiere autenticación")
        else:
            print(f"   ⚠️ Inesperado: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico completado")

if __name__ == "__main__":
    diagnosticar_auth()
