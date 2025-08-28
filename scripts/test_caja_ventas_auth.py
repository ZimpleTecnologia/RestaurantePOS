#!/usr/bin/env python3
"""
Script para probar el módulo Caja y Ventas con autenticación
"""
import sys
import os
import requests
import json
from decimal import Decimal

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
CAJA_VENTAS_URL = f"{BASE_URL}/api/v1/caja-ventas"

def login():
    """Hacer login y obtener token"""
    print("🔐 Iniciando sesión...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, data=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login exitoso - Token obtenido")
            return token
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_caja_ventas_with_auth(token):
    """Probar endpoints de caja y ventas con autenticación"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🧪 Probando endpoints de Caja y Ventas...")
    
    # 1. Obtener estado
    print("\n1️⃣ Probando GET /estado...")
    try:
        response = requests.get(f"{CAJA_VENTAS_URL}/estado", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Estado obtenido:")
            print(f"   - Sesión activa: {data.get('sesion_activa')}")
            print(f"   - Puede vender: {data.get('puede_vender')}")
            if data.get('sesion_activa_info'):
                print(f"   - Sesión: {data['sesion_activa_info']['session_number']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Probar apertura de caja
    print("\n2️⃣ Probando POST /abrir-caja...")
    try:
        apertura_data = {
            "password": "5678",
            "fondo_inicial": 1000.00,
            "notas_apertura": "Apertura de prueba desde script"
        }
        response = requests.post(f"{CAJA_VENTAS_URL}/abrir-caja", 
                               headers=headers, 
                               json=apertura_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Caja abierta exitosamente:")
            print(f"   - Sesión: {data['sesion']['session_number']}")
            print(f"   - Fondo inicial: ${data['sesion']['fondo_inicial']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Obtener movimientos
    print("\n3️⃣ Probando GET /movimientos...")
    try:
        response = requests.get(f"{CAJA_VENTAS_URL}/movimientos", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            movimientos = response.json()
            print(f"✅ Movimientos obtenidos: {len(movimientos)} registros")
            for mov in movimientos[:3]:  # Mostrar solo los primeros 3
                print(f"   - {mov['tipo']}: ${mov['monto']} - {mov['descripcion']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("=" * 80)
    print("🧪 PRUEBAS DE AUTENTICACIÓN - MÓDULO CAJA Y VENTAS")
    print("=" * 80)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print("✅ Servidor detectado en http://localhost:8000")
    except:
        print("❌ No se puede conectar al servidor en http://localhost:8000")
        print("   Asegúrate de que el servidor esté corriendo con: uvicorn app.main:app --reload")
        return
    
    # Hacer login
    token = login()
    if not token:
        print("❌ No se pudo obtener el token de autenticación")
        return
    
    # Probar endpoints
    test_caja_ventas_with_auth(token)
    
    print("\n" + "=" * 80)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    main()
