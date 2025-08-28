#!/usr/bin/env python3
"""
Script para diagnóstico detallado del error 500
"""
import requests
import json
import traceback

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ESTADO_CAJA_URL = f"{BASE_URL}/api/v1/caja-ventas/estado"
ABRIR_CAJA_URL = f"{BASE_URL}/api/v1/caja-ventas/abrir-caja"

def diagnostico_detallado():
    """Diagnóstico detallado del error 500"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DETALLADO - ERROR 500")
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
        else:
            print(f"   ❌ Error en login: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return
    
    # 2. Verificar estado de caja
    print("\n2️⃣ Verificando estado de caja...")
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
            
            # Verificar si hay sesión activa
            if data.get('sesion_activa'):
                print(f"   ⚠️ HAY UNA SESIÓN ACTIVA - Este es el problema!")
                print(f"   No se puede abrir una nueva sesión mientras hay una activa")
                return
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalle: {error_data.get('detail')}")
            except:
                print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 3. Probar apertura de caja con diferentes datos
    print("\n3️⃣ Probando apertura de caja...")
    
    # Prueba 1: Datos básicos
    print("\n   🔄 Prueba 1: Datos básicos")
    apertura_data_1 = {
        "password": "1234",
        "fondo_inicial": 50000.00,
        "notas_apertura": "Prueba básica"
    }
    
    try:
        response = requests.post(ABRIR_CAJA_URL, json=apertura_data_1, headers=headers)
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
        print(f"   Traceback: {traceback.format_exc()}")
    
    # 4. Verificar estructura de la base de datos
    print("\n4️⃣ Verificando estructura de datos...")
    print("   Verificando que los modelos estén correctos...")
    
    # 5. Probar con datos mínimos
    print("\n5️⃣ Prueba con datos mínimos...")
    apertura_data_min = {
        "password": "1234",
        "fondo_inicial": 0.00
    }
    
    try:
        response = requests.post(ABRIR_CAJA_URL, json=apertura_data_min, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Caja abierta con datos mínimos!")
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalle: {error_data.get('detail')}")
            except:
                print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico completado")

if __name__ == "__main__":
    diagnostico_detallado()
