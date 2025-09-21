import requests
import json

def debug_menus_detailed():
    """Debug detallado del endpoint de menús"""
    print("🔍 Debug detallado del endpoint de menús...")
    print("=" * 60)
    
    # Probar endpoint de menús con diferentes parámetros
    endpoints_to_test = [
        "http://127.0.0.1:8000/api/v1/restaurant-menu/menus/",
        "http://127.0.0.1:8000/api/v1/restaurant-menu/menus/?limit=5",
        "http://127.0.0.1:8000/api/v1/restaurant-menu/menus/?activo=true",
        "http://127.0.0.1:8000/api/v1/restaurant-menu/menus/?publicado=true"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n📋 Probando: {endpoint}")
        try:
            response = requests.get(endpoint)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Funcionando")
                print(f"Total: {data.get('total', 0)}")
                print(f"Menús: {len(data.get('menus', []))}")
            else:
                print(f"❌ Error {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
    
    # Probar endpoint de debug que sabemos que funciona
    print(f"\n📋 Probando endpoint de debug (que funciona):")
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/test/menu-hoy-simple")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Debug funcionando")
            print(f"Data: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_menus_detailed()


