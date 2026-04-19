#!/usr/bin/env python3
"""
Script para probar los endpoints corregidos
"""
import requests
import json

def test_endpoints_fixed():
    """Probar los endpoints corregidos"""
    print("🔍 Probando endpoints corregidos...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de categorías
    print("\n📋 Probando categorías...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categorías: {len(data.get('categorias', []))}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de platos
    print("\n🍽️ Probando platos...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/platos/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Platos: {len(data.get('platos', []))}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de menús
    print("\n📅 Probando menús...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menús: {len(data.get('menus', []))}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de acompañamientos
    print("\n🥗 Probando acompañamientos...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/acompanamientos/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Acompañamientos: {len(data.get('acompanamientos', []))}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints_fixed()


