import requests
import json

def debug_menus_endpoint():
    """Debug específico del endpoint de menús"""
    print("🔍 Debug del endpoint de menús...")
    print("=" * 50)
    
    try:
        # Probar endpoint con debug
        response = requests.get("http://127.0.0.1:8000/api/v1/restaurant-menu/menus/")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("❌ Error 500 - Internal Server Error")
            print(f"Response text: {response.text}")
        elif response.status_code == 200:
            data = response.json()
            print("✅ Endpoint funcionando")
            print(f"Total: {data.get('total', 0)}")
            print(f"Menús: {len(data.get('menus', []))}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Probar endpoint de debug simple
    print("\n🔍 Probando endpoint de debug...")
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/test/menu-hoy-simple")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de debug funcionando")
            print(f"Data: {data}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    debug_menus_endpoint()


