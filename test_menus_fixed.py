import requests
import json

def test_menus_fixed():
    """Probar endpoints de menús después de la corrección"""
    print("🔍 Probando endpoints de menús corregidos...")
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
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menus_fixed()


