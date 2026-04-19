import requests

def test_menus_simple():
    """Probar solo el endpoint de menús"""
    print("🔍 Probando endpoint de menús...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/restaurant-menu/menus/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint funcionando")
            print(f"Total: {data.get('total', 0)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menus_simple()


