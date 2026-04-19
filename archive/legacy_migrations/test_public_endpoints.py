#!/usr/bin/env python3
"""
Script para probar los endpoints públicos de menús
"""
import requests
import json
from datetime import date

def test_public_endpoints():
    """Probar los endpoints públicos de menús"""
    print("🔍 Probando endpoints públicos de menús...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Probar obtener platos
        print("\n📋 Probando GET /api/v1/public/menus/platos/")
        response = requests.get(f"{base_url}/api/v1/public/menus/platos/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Platos obtenidos: {len(data)} platos")
            if data:
                print(f"   Primer plato: {data[0].get('nombre', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
        
        # 2. Probar crear un plato
        print("\n🍽️ Probando POST /api/v1/public/menus/platos/")
        plato_data = {
            "nombre": "Plato de Prueba",
            "descripcion": "Plato creado para probar el endpoint",
            "precio": 15000.0,
            "tipo": "Variable",
            "categoria": "Plato Principal"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/public/menus/platos/",
            json=plato_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Plato creado: {data}")
            plato_id = data.get('plato_id')
        else:
            print(f"❌ Error: {response.text}")
            plato_id = None
        
        # 3. Probar obtener menús
        print("\n📅 Probando GET /api/v1/public/menus/")
        response = requests.get(f"{base_url}/api/v1/public/menus/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menús obtenidos: {len(data)} menús")
        else:
            print(f"❌ Error: {response.text}")
        
        # 4. Probar crear un menú
        print("\n📋 Probando POST /api/v1/public/menus/")
        menu_data = {
            "fecha": str(date.today()),
            "nombre": "Menú de Prueba",
            "descripcion": "Menú creado para probar el endpoint",
            "plato_ids": [plato_id] if plato_id else []
        }
        
        response = requests.post(
            f"{base_url}/api/v1/public/menus/",
            json=menu_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menú creado: {data}")
        else:
            print(f"❌ Error: {response.text}")
        
        # 5. Probar menú de hoy
        print("\n📅 Probando GET /api/v1/public/menus/hoy/menu")
        response = requests.get(f"{base_url}/api/v1/public/menus/hoy/menu")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menú de hoy: {data}")
        else:
            print(f"❌ Error: {response.text}")
        
        # 6. Probar estadísticas
        print("\n📊 Probando GET /api/v1/public/menus/stats")
        response = requests.get(f"{base_url}/api/v1/public/menus/stats")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Estadísticas: {data}")
        else:
            print(f"❌ Error: {response.text}")
        
        print("\n🎉 Pruebas de endpoints públicos completadas!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_public_endpoints()


