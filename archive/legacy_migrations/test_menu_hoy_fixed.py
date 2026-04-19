import requests
import json

def test_menu_hoy_fixed():
    """Probar endpoint de menú de hoy corregido"""
    print("🔍 Probando endpoint de menú de hoy corregido...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de menú de hoy
    print("\n📅 Probando menú de hoy...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/hoy")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('menu'):
                print(f"✅ Menú de hoy: {data['menu'].get('nombre', 'N/A')}")
                print(f"   ID: {data['menu'].get('id', 'N/A')}")
                print(f"   Fecha: {data['menu'].get('fecha', 'N/A')}")
                print(f"   Precio: {data['menu'].get('precio', 'N/A')}")
                print(f"   Categorías: {len(data.get('categorias', {}))}")
                print(f"   Acompañamientos: {len(data.get('acompanamientos_fijos', []))}")
                print(f"   Platos fijos: {len(data.get('platos_fijos', []))}")
            else:
                print(f"⚠️ {data.get('mensaje', 'No hay menú para hoy')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar todos los endpoints principales
    print("\n📋 Probando todos los endpoints principales...")
    endpoints = [
        ("/api/v1/restaurant-menu/categorias/", "Categorías"),
        ("/api/v1/restaurant-menu/platos/", "Platos"),
        ("/api/v1/restaurant-menu/menus/", "Menús"),
        ("/api/v1/restaurant-menu/acompanamientos/", "Acompañamientos")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', len(data.get('items', [])))
                print(f"✅ {name}: {total}")
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")

if __name__ == "__main__":
    test_menu_hoy_fixed()


