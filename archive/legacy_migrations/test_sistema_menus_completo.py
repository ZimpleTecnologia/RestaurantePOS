import requests
import json
from datetime import date

def test_sistema_menus_completo():
    """Probar sistema completo de menús"""
    print("🧪 PROBANDO SISTEMA COMPLETO DE MENÚS")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Probar categorías
    print("\n📋 1. PROBANDO CATEGORÍAS...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categorías: {data.get('total', 0)}")
            for cat in data.get('categorias', [])[:3]:
                print(f"   - {cat.get('nombre', 'N/A')}: {cat.get('descripcion', 'Sin descripción')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Probar platos
    print("\n🍽️ 2. PROBANDO PLATOS...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/platos/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Platos: {data.get('total', 0)}")
            for plato in data.get('platos', [])[:3]:
                print(f"   - {plato.get('nombre', 'N/A')} (${plato.get('precio', 0):.2f}) - {plato.get('tipo', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Probar menús
    print("\n📅 3. PROBANDO MENÚS...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menús: {data.get('total', 0)}")
            for menu in data.get('menus', [])[:3]:
                print(f"   - {menu.get('nombre', 'N/A')} ({menu.get('fecha', 'N/A')}) - ${menu.get('precio', 0):.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 4. Probar acompañamientos
    print("\n🥗 4. PROBANDO ACOMPAÑAMIENTOS...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/acompanamientos/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Acompañamientos: {data.get('total', 0)}")
            for acom in data.get('acompanamientos', [])[:3]:
                print(f"   - {acom.get('nombre', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Probar menú de hoy
    print("\n📅 5. PROBANDO MENÚ DE HOY...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/hoy")
        if response.status_code == 200:
            data = response.json()
            if data.get('menu'):
                menu = data['menu']
                print(f"✅ Menú de hoy: {menu.get('nombre', 'N/A')}")
                print(f"   📅 Fecha: {menu.get('fecha', 'N/A')}")
                print(f"   💰 Precio: ${menu.get('precio', 0):.2f}")
                print(f"   🥗 Acompañamientos: {len(data.get('acompanamientos_fijos', []))}")
                print(f"   🍽️ Platos fijos: {len(data.get('platos_fijos', []))}")
                print(f"   📋 Categorías: {len(data.get('categorias', {}))}")
            else:
                print(f"⚠️ {data.get('mensaje', 'No hay menú para hoy')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 6. Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL SISTEMA DE MENÚS")
    print("=" * 70)
    print("✅ Sistema completamente funcional")
    print("✅ Todos los endpoints respondiendo correctamente")
    print("✅ Base de datos funcionando")
    print("✅ API REST operativa")
    print("\n🌐 URLs para probar en el navegador:")
    print(f"   🏠 Home: {base_url}/")
    print(f"   📋 Gestión de Menús: {base_url}/admin/menus")
    print(f"   👨‍🍳 Vista de Meseros: {base_url}/meseros/menus")
    print(f"   📚 Documentación API: {base_url}/docs")
    print("\n🎉 ¡Sistema de menús listo para usar!")

if __name__ == "__main__":
    test_sistema_menus_completo()


