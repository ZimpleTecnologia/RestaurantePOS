#!/usr/bin/env python3
"""
Script para cerrar la sesión de caja existente
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ESTADO_CAJA_URL = f"{BASE_URL}/api/v1/caja-ventas/estado"
CERRAR_CAJA_URL = f"{BASE_URL}/api/v1/caja-ventas/cerrar-caja"

def cerrar_sesion_caja():
    """Cerrar la sesión de caja existente"""
    print("=" * 60)
    print("🔒 CERRAR SESIÓN DE CAJA")
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
            print(f"   ✅ Login exitoso!")
        else:
            print(f"   ❌ Error en login: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return
    
    # 2. Verificar estado actual
    print("\n2️⃣ Verificando estado actual...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(ESTADO_CAJA_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   Sesión activa: {data.get('sesion_activa')}")
            
            if data.get('sesion_activa'):
                print(f"   ✅ Hay una sesión activa, procediendo a cerrarla...")
            else:
                print(f"   ℹ️ No hay sesión activa")
                return
        else:
            print(f"   ❌ Error obteniendo estado: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return
    
    # 3. Cerrar sesión
    print("\n3️⃣ Cerrando sesión...")
    cierre_data = {
        "password": "1234",
        "monto_contado": 50000.00,  # Mismo monto que se usó para abrir
        "notas_cierre": "Cierre automático desde script"
    }
    
    try:
        response = requests.post(CERRAR_CAJA_URL, json=cierre_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sesión cerrada exitosamente!")
            print(f"   Mensaje: {data.get('message')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalle: {error_data.get('detail')}")
            except:
                print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 4. Verificar estado final
    print("\n4️⃣ Verificando estado final...")
    try:
        response = requests.get(ESTADO_CAJA_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   Sesión activa: {data.get('sesion_activa')}")
            if not data.get('sesion_activa'):
                print(f"   ✅ Sesión cerrada correctamente!")
            else:
                print(f"   ⚠️ La sesión sigue activa")
        else:
            print(f"   ❌ Error verificando estado final: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Proceso completado")

if __name__ == "__main__":
    cerrar_sesion_caja()
