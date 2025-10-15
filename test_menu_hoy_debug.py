import requests
import json

def test_menu_hoy_debug():
    """Probar endpoint de debug del menú de hoy"""
    print("🔍 Probando endpoint de debug del menú de hoy...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de debug del menú de hoy
    print("\n📅 Probando menú de hoy (debug)...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug/menu-hoy-debug")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('menu'):
                print(f"✅ Menú de hoy encontrado: {data['menu'].get('nombre', 'N/A')}")
                print(f"   ID: {data['menu'].get('id', 'N/A')}")
                print(f"   Fecha: {data['menu'].get('fecha', 'N/A')}")
                print(f"   Precio: {data['menu'].get('precio', 'N/A')}")
                print(f"   Estado: {data['menu'].get('estado', 'N/A')}")
            else:
                print(f"⚠️ {data.get('mensaje', 'No hay menú para hoy')}")
                print(f"   Fecha buscada: {data.get('fecha_buscada', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint original del menú de hoy
    print("\n📅 Probando menú de hoy (original)...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/hoy")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('menu'):
                print(f"✅ Menú de hoy (original): {data['menu'].get('nombre', 'N/A')}")
            else:
                print(f"⚠️ {data.get('mensaje', 'No hay menú para hoy')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menu_hoy_debug()


