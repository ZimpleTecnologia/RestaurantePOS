#!/usr/bin/env python3
"""
Script para probar endpoints de debug
"""
import requests
import json

def test_debug_endpoints():
    """Probar endpoints de debug para identificar el problema"""
    print("🔍 Probando endpoints de debug...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint simple con ORM
    print("\n📋 Probando endpoint simple con ORM...")
    try:
        response = requests.get(f"{base_url}/api/v1/test/categorias-simple")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint simple funcionando")
            print(f"Categorías: {len(data.get('categorias', []))}")
            for cat in data.get('categorias', [])[:3]:
                print(f"   - {cat.get('nombre', 'N/A')} (ID: {cat.get('id', 'N/A')})")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint con consulta raw
    print("\n📋 Probando endpoint con consulta raw...")
    try:
        response = requests.get(f"{base_url}/api/v1/test/categorias-raw")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint raw funcionando")
            print(f"Categorías: {len(data.get('categorias', []))}")
            for cat in data.get('categorias', [])[:3]:
                print(f"   - {cat.get('nombre', 'N/A')} (ID: {cat.get('id', 'N/A')})")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de schema test
    print("\n📋 Probando endpoint de schema test...")
    try:
        response = requests.get(f"{base_url}/api/v1/test/categorias-schema-test")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint schema test funcionando")
            if data.get('success'):
                print(f"Categoría: {data.get('categoria', {}).get('nombre', 'N/A')}")
            else:
                print(f"Error: {data.get('error', 'N/A')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint exact copy
    print("\n📋 Probando endpoint exact copy...")
    try:
        response = requests.get(f"{base_url}/api/v1/test/categorias-exact-copy")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint exact copy funcionando")
            print(f"Categorías: {len(data.get('categorias', []))}")
            print(f"Total: {data.get('total', 0)}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint original
    print("\n📋 Probando endpoint original...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint original funcionando")
            print(f"Categorías: {len(data.get('categorias', []))}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_debug_endpoints()
