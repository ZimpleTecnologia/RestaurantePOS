import requests
import json

def test_menus_sql():
    """Probar endpoints de menús usando SQL directo"""
    print("🔍 Probando endpoints de menús con SQL directo...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de conteo SQL
    print("\n📊 Probando conteo de menús (SQL)...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug-sql/menus-count")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conteo SQL: {data.get('count', 0)}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de primer menú SQL
    print("\n📋 Probando primer menú (SQL)...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug-sql/menus-first")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Primer menú SQL: {data}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar endpoint de menús raw SQL
    print("\n📋 Probando menús raw (SQL)...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug-sql/menus-raw")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menús raw SQL: {len(data.get('menus', []))} menús")
            for menu in data.get('menus', [])[:2]:  # Mostrar solo 2
                print(f"   - {menu.get('nombre', 'N/A')} (ID: {menu.get('menu_id', 'N/A')})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menus_sql()
