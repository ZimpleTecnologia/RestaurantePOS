import requests
import json

def test_menus_final_corrected():
    """Probar endpoints de menús después de la corrección de la base de datos"""
    print("🔍 Probando endpoints de menús - corrección final...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de debug
    print("\n📊 Probando conteo de menús...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug/menus-count")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conteo: {data.get('count', 0)}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de primer menú
    print("\n📋 Probando primer menú...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug/menus-first")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Primer menú: {data}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de menús raw
    print("\n📋 Probando menús raw...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug/menus-raw")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menús raw: {len(data.get('menus', []))} menús")
            for menu in data.get('menus', [])[:2]:  # Mostrar solo 2
                print(f"   - {menu.get('nombre', 'N/A')} (ID: {menu.get('id', 'N/A')})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint principal de menús
    print("\n📋 Probando endpoint principal de menús...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint principal funcionando")
            print(f"Total: {data.get('total', 0)}")
            print(f"Menús: {len(data.get('menus', []))}")
            for menu in data.get('menus', [])[:2]:  # Mostrar solo 2
                print(f"   - {menu.get('nombre', 'N/A')} (ID: {menu.get('id', 'N/A')})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de menú de hoy
    print("\n📅 Probando menú de hoy...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/hoy")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('menu'):
                print(f"✅ Menú de hoy: {data['menu'].get('nombre', 'N/A')}")
            else:
                print(f"⚠️ {data.get('mensaje', 'No hay menú para hoy')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menus_final_corrected()


