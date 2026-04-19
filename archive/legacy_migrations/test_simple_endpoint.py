#!/usr/bin/env python3
"""
Script para probar un endpoint simple sin schemas complejos
"""
import requests
import json

def test_simple_endpoint():
    """Probar un endpoint simple para identificar el problema"""
    print("🔍 Probando endpoint simple...")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de salud primero
    print("\n🏥 Probando endpoint de salud...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Servidor funcionando")
        else:
            print("❌ Problema con el servidor")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Probar endpoint de documentación
    print("\n📚 Probando documentación...")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Documentación disponible")
        else:
            print("❌ Documentación no disponible")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de API info
    print("\n📋 Probando API info...")
    try:
        response = requests.get(f"{base_url}/api/v1/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ API info disponible")
            print(f"Endpoints disponibles: {list(data.get('endpoints', {}).keys())}")
        else:
            print("❌ API info no disponible")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de categorías con timeout corto
    print("\n📋 Probando endpoint de categorías...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('content-length', 'N/A')}")
        
        if response.status_code == 200:
            print("✅ Endpoint funcionando")
            try:
                data = response.json()
                print(f"Datos recibidos: {data}")
            except Exception as e:
                print(f"❌ Error parseando JSON: {e}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - El endpoint no responde en 5 segundos")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_endpoint()


