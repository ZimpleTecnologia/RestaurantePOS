import requests
import json

def test_menus_sql_simple():
    """Probar endpoint SQL simple"""
    print("🔍 Probando endpoint SQL simple...")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint SQL
    print("\n📋 Probando menús con SQL directo...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug/menus-sql")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menús SQL: {len(data.get('menus', []))} menús")
            for menu in data.get('menus', [])[:2]:  # Mostrar solo 2
                print(f"   - {menu.get('nombre', 'N/A')} (ID: {menu.get('menu_id', 'N/A')})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menus_sql_simple()


