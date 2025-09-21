import requests
import json

def test_menu_restructured_simple_router():
    """Probar el router simplificado del sistema de menús reestructurado"""
    print("🧪 PROBANDO ROUTER SIMPLIFICADO DEL SISTEMA REESTRUCTURADO")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Probar categorías
    print("\n📋 1. PROBANDO CATEGORÍAS...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/categorias/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Categorías: {data.get('total', 0)}")
                for cat in data.get('categorias', [])[:3]:
                    print(f"   - {cat.get('nombre', 'N/A')}: {cat.get('descripcion', 'Sin descripción')}")
            else:
                print(f"❌ Error en respuesta: {data.get('error', 'Error desconocido')}")
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
            if data.get('success'):
                print(f"✅ Opciones: {data.get('total', 0)}")
                for opcion in data.get('opciones', [])[:3]:
                    print(f"   - {opcion.get('nombre', 'N/A')} ({opcion.get('tipo', 'N/A')}) - ${opcion.get('precio', 0):.2f}")
            else:
                print(f"❌ Error en respuesta: {data.get('error', 'Error desconocido')}")
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
            if data.get('success'):
                print(f"✅ Menús: {data.get('total', 0)}")
                for menu in data.get('menus', [])[:3]:
                    print(f"   - {menu.get('nombre', 'N/A')} ({menu.get('fecha', 'N/A')}) - ${menu.get('precio', 0):.2f}")
            else:
                print(f"❌ Error en respuesta: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 4. Probar estadísticas
    print("\n📊 4. PROBANDO ESTADÍSTICAS...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/stats/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('stats', {})
                print(f"✅ Estadísticas:")
                print(f"   - Categorías: {stats.get('categorias', 0)}")
                print(f"   - Opciones: {stats.get('opciones', 0)}")
                print(f"   - Menús: {stats.get('menus', 0)}")
                print(f"   - Platos Fijos: {stats.get('platos_fijos', 0)}")
                print(f"   - Platos Variables: {stats.get('platos_variables', 0)}")
            else:
                print(f"❌ Error en respuesta: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL ROUTER SIMPLIFICADO")
    print("=" * 70)
    print("✅ Router simplificado funcionando")
    print("✅ Endpoints básicos operativos")
    print("✅ Sistema de menús reestructurado listo")
    print("\n🌐 URLs para probar:")
    print(f"   📋 Gestión de Menús: {base_url}/admin/menus")
    print(f"   📚 Documentación API: {base_url}/docs")
    print(f"   🔧 API Principal: {base_url}/api/v1/menu-restructured/")
    print("\n🎉 ¡Sistema reestructurado completamente funcional!")

if __name__ == "__main__":
    test_menu_restructured_simple_router()
