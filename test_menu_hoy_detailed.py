import requests
import json

def test_menu_hoy_detailed():
    """Probar endpoint detallado del menú de hoy"""
    print("🔍 Probando endpoint detallado del menú de hoy...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint detallado
    print("\n📅 Probando menú de hoy (detallado)...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug/menu-hoy-detailed")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('menu'):
                print(f"✅ Menú de hoy encontrado: {data['menu'].get('nombre', 'N/A')}")
                print(f"   ID: {data['menu'].get('id', 'N/A')}")
                print(f"   Fecha: {data['menu'].get('fecha', 'N/A')}")
                print(f"   Precio: {data['menu'].get('precio', 'N/A')}")
                print(f"   Estado: {data['menu'].get('estado', 'N/A')}")
                print(f"   Categorías: {len(data.get('categorias', {}))}")
                print(f"   Acompañamientos: {len(data.get('acompanamientos_fijos', []))}")
                print(f"   Platos fijos: {len(data.get('platos_fijos', []))}")
            else:
                print(f"⚠️ {data.get('mensaje', 'No hay menú para hoy')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menu_hoy_detailed()


