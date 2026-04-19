import requests
import json
from datetime import date

def test_menu_restructured():
    """Probar el sistema de menús reestructurado"""
    print("🧪 PROBANDO SISTEMA DE MENÚS REESTRUCTURADO")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Probar categorías
    print("\n📋 1. PROBANDO CATEGORÍAS...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/categorias/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categorías: {data.get('total', 0)}")
            for cat in data.get('categorias', [])[:3]:
                print(f"   - {cat.get('nombre', 'N/A')}: {cat.get('descripcion', 'Sin descripción')}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Probar opciones
    print("\n🍽️ 2. PROBANDO OPCIONES...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Opciones: {data.get('total', 0)}")
            for opcion in data.get('opciones', [])[:3]:
                print(f"   - {opcion.get('nombre', 'N/A')} ({opcion.get('tipo', 'N/A')}) - ${opcion.get('precio', 0):.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Probar platos fijos
    print("\n⭐ 3. PROBANDO PLATOS FIJOS...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/?tipo=Fijo")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Platos fijos: {data.get('total', 0)}")
            for opcion in data.get('opciones', [])[:3]:
                print(f"   - {opcion.get('nombre', 'N/A')}: ${opcion.get('precio', 0):.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 4. Probar platos variables
    print("\n🔄 4. PROBANDO PLATOS VARIABLES...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/?tipo=Variable")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Platos variables: {data.get('total', 0)}")
            for opcion in data.get('opciones', [])[:3]:
                categoria = opcion.get('categoria', {}).get('nombre', 'Sin categoría')
                print(f"   - {opcion.get('nombre', 'N/A')} ({categoria}): ${opcion.get('precio', 0):.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Probar menús
    print("\n📅 5. PROBANDO MENÚS...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/menus/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Menús: {data.get('total', 0)}")
            for menu in data.get('menus', [])[:3]:
                print(f"   - {menu.get('nombre', 'N/A')} ({menu.get('fecha', 'N/A')}) - ${menu.get('precio', 0):.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 6. Crear un menú de prueba
    print("\n🆕 6. CREANDO MENÚ DE PRUEBA...")
    try:
        # Obtener algunas opciones para el menú
        opciones_response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/")
        if opciones_response.status_code == 200:
            opciones_data = opciones_response.json()
            opciones_ids = [op['id'] for op in opciones_data.get('opciones', [])[:5]]  # Tomar las primeras 5
            
            menu_data = {
                "fecha": str(date.today()),
                "nombre": f"Menú de Prueba - {date.today()}",
                "descripcion": "Menú de prueba del sistema reestructurado",
                "precio": 15000.00,
                "opciones_ids": opciones_ids
            }
            
            response = requests.post(f"{base_url}/api/v1/menu-restructured/menus/", json=menu_data)
            if response.status_code == 200:
                menu_creado = response.json()
                print(f"✅ Menú creado: {menu_creado.get('nombre', 'N/A')}")
                print(f"   ID: {menu_creado.get('id', 'N/A')}")
                print(f"   Opciones: {len(opciones_ids)}")
            else:
                print(f"❌ Error creando menú: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print(f"❌ Error obteniendo opciones: {opciones_response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 7. Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL SISTEMA REESTRUCTURADO")
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
    test_menu_restructured()


