#!/usr/bin/env python3
"""
Script para probar el endpoint de menú de hoy
"""
import requests
import json

def test_menu_hoy():
    """Probar el endpoint de menú de hoy"""
    print("🔍 Probando endpoint de menú de hoy...")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint simple primero
    print("\n📋 Probando endpoint simple...")
    try:
        response = requests.get(f"{base_url}/api/v1/test/menu-hoy-simple")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint simple funcionando")
            if data.get('menu'):
                print(f"Menú: {data.get('menu', {}).get('nombre', 'N/A')}")
            else:
                print(f"Mensaje: {data.get('mensaje', 'N/A')}")
                print(f"Fecha buscada: {data.get('fecha_buscada', 'N/A')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint original
    print("\n📋 Probando endpoint original...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/hoy")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint original funcionando")
            if data.get('menu'):
                print(f"Menú: {data.get('menu', {}).get('nombre', 'N/A')}")
                print(f"Categorías: {list(data.get('categorias', {}).keys())}")
                print(f"Acompañamientos: {len(data.get('acompanamientos_fijos', []))}")
                print(f"Platos fijos: {len(data.get('platos_fijos', []))}")
            else:
                print(f"Mensaje: {data.get('mensaje', 'N/A')}")
        elif response.status_code == 404:
            print("⚠️ No hay menú publicado para hoy")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menu_hoy()
