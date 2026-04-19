#!/usr/bin/env python3
"""
Script simple para probar el nuevo sistema de menús del restaurante
"""
import requests
import json
from datetime import date

def test_restaurant_menu_endpoints():
    """Probar los endpoints del sistema de menús del restaurante"""
    print("🍽️ Probando sistema de menús del restaurante...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Probar obtener categorías
        print("\n📋 Probando GET /api/v1/restaurant-menu/categorias/")
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categorías obtenidas: {data.get('total', 0)} categorías")
            for categoria in data.get('categorias', []):
                print(f"   - {categoria.get('nombre', 'N/A')}: {categoria.get('descripcion', 'Sin descripción')}")
        else:
            print(f"❌ Error: {response.text}")
        
        # 2. Probar obtener platos
        print("\n🍽️ Probando GET /api/v1/restaurant-menu/platos/")
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/platos/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Platos obtenidos: {data.get('total', 0)} platos")
            for plato in data.get('platos', [])[:3]:  # Mostrar solo los primeros 3
                print(f"   - {plato.get('nombre', 'N/A')}: ${plato.get('precio', 0)} ({plato.get('tipo', 'N/A')})")
        else:
            print(f"❌ Error: {response.text}")
        
        # 3. Probar obtener acompañamientos fijos
        print("\n🥗 Probando GET /api/v1/restaurant-menu/acompanamientos/")
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/acompanamientos/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Acompañamientos obtenidos: {data.get('total', 0)} acompañamientos")
            for acompanamiento in data.get('acompanamientos', []):
                print(f"   - {acompanamiento.get('nombre', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
        
        # 4. Probar obtener menús
        print("\n📅 Probando GET /api/v1/restaurant-menu/menus/")
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menús obtenidos: {data.get('total', 0)} menús")
        else:
            print(f"❌ Error: {response.text}")
        
        # 5. Probar menú de hoy
        print("\n📅 Probando GET /api/v1/restaurant-menu/menus/hoy")
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/hoy")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menú de hoy obtenido: {data.get('menu', {}).get('nombre', 'N/A')}")
            print(f"   Categorías disponibles: {list(data.get('categorias', {}).keys())}")
            print(f"   Acompañamientos fijos: {len(data.get('acompanamientos_fijos', []))}")
            print(f"   Platos fijos: {len(data.get('platos_fijos', []))}")
        elif response.status_code == 404:
            print("⚠️ No hay menú publicado para hoy")
        else:
            print(f"❌ Error: {response.text}")
        
        print("\n🎉 Pruebas del sistema de menús del restaurante completadas!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_restaurant_menu_endpoints()


