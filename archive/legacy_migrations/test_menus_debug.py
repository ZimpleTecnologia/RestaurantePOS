import requests
import json

def test_menus_debug():
    """Probar específicamente el endpoint de menús con debug"""
    print("🔍 Probando endpoint de menús con debug...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de menús
    print("\n📅 Probando endpoint de menús...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de menús funcionando")
            print(f"Total menús: {data.get('total', 0)}")
            for menu in data.get('menus', [])[:3]:  # Mostrar solo 3
                print(f"   - {menu.get('nombre', 'N/A')} ({menu.get('fecha', 'N/A')})")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de menús con parámetros
    print("\n📅 Probando endpoint de menús con parámetros...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/?limit=5")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint con parámetros funcionando")
            print(f"Total menús: {data.get('total', 0)}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de menús de hoy
    print("\n📅 Probando endpoint de menú de hoy...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/hoy")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('menu'):
                print("✅ Menú de hoy encontrado")
                print(f"Menú: {data['menu'].get('nombre', 'N/A')}")
            else:
                print(f"⚠️ {data.get('mensaje', 'No hay menú para hoy')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menus_debug()


