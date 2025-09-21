import requests
import json

def test_debug_menus():
    """Probar endpoints de debug de menús"""
    print("🔍 Probando endpoints de debug de menús...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de conteo
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
                print(f"   - {menu.get('nombre', 'N/A')} (ID: {menu.get('menu_id', 'N/A')})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_debug_menus()


