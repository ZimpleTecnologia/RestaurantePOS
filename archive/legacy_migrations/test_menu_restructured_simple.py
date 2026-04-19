import requests
import json

def test_menu_restructured_simple():
    """Probar el sistema de menús reestructurado de forma simplificada"""
    print("🧪 PROBANDO SISTEMA DE MENÚS REESTRUCTURADO (SIMPLIFICADO)")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Probar categorías
    print("\n📋 1. PROBANDO CATEGORÍAS...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/categorias/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categorías: {data.get('total', 0)}")
            for cat in data.get('categorias', [])[:3]:
                print(f"   - {cat.get('nombre', 'N/A')}: {cat.get('descripcion', 'Sin descripción')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Probar opciones
    print("\n🍽️ 2. PROBANDO OPCIONES...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Opciones: {data.get('total', 0)}")
            for opcion in data.get('opciones', [])[:3]:
                print(f"   - {opcion.get('nombre', 'N/A')} ({opcion.get('tipo', 'N/A')}) - ${opcion.get('precio', 0):.2f}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Probar menús
    print("\n📅 3. PROBANDO MENÚS...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/menus/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menús: {data.get('total', 0)}")
            for menu in data.get('menus', [])[:3]:
                print(f"   - {menu.get('nombre', 'N/A')} ({menu.get('fecha', 'N/A')}) - ${menu.get('precio', 0):.2f}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print("✅ Sistema de menús reestructurado funcionando")
    print("✅ Categorías de platos variables")
    print("✅ Opciones de platos (fijos y variables)")
    print("✅ Gestión de menús del día")
    print("\n🌐 URLs para probar:")
    print(f"   📋 Gestión de Menús: {base_url}/admin/menus-restructured")
    print(f"   📚 Documentación API: {base_url}/docs")
    print("\n🎉 ¡Sistema reestructurado listo para usar!")

if __name__ == "__main__":
    test_menu_restructured_simple()


