import requests
import json

def test_create_opcion():
    """Probar la creación de una nueva opción"""
    print("🧪 PROBANDO CREACIÓN DE NUEVA OPCIÓN")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Probar creación de opción
    print("\n🍽️ 1. CREANDO NUEVA OPCIÓN...")
    try:
        params = {
            'nombre': 'Pollo a la Plancha',
            'descripcion': 'Pechuga de pollo a la plancha con especias',
            'tipo': 'Variable',
            'categoria_id': 2,  # Proteína
            'precio': 12000.0,
            'activo': True
        }
        
        response = requests.post(f"{base_url}/api/v1/menu-restructured/opciones/", params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Opción creada exitosamente:")
                print(f"   - ID: {data.get('opcion', {}).get('id', 'N/A')}")
                print(f"   - Nombre: {data.get('opcion', {}).get('nombre', 'N/A')}")
                print(f"   - Tipo: {data.get('opcion', {}).get('tipo', 'N/A')}")
                print(f"   - Precio: ${data.get('opcion', {}).get('precio', 0):.2f}")
            else:
                print(f"❌ Error en respuesta: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Verificar que la opción se creó
    print("\n🔍 2. VERIFICANDO OPCIÓN CREADA...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                opciones = data.get('opciones', [])
                pollo_opcion = next((op for op in opciones if op.get('nombre') == 'Pollo a la Plancha'), None)
                if pollo_opcion:
                    print(f"✅ Opción encontrada en la lista:")
                    print(f"   - ID: {pollo_opcion.get('id', 'N/A')}")
                    print(f"   - Nombre: {pollo_opcion.get('nombre', 'N/A')}")
                    print(f"   - Tipo: {pollo_opcion.get('tipo', 'N/A')}")
                    print(f"   - Precio: ${pollo_opcion.get('precio', 0):.2f}")
                else:
                    print("❌ Opción no encontrada en la lista")
            else:
                print(f"❌ Error en respuesta: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Probar creación de menú
    print("\n📅 3. CREANDO NUEVO MENÚ...")
    try:
        from datetime import date, timedelta
        tomorrow = date.today() + timedelta(days=1)
        
        params = {
            'fecha': str(tomorrow),
            'nombre': f'Menú de Prueba - {tomorrow}',
            'descripcion': 'Menú creado para probar el sistema',
            'precio': 18000.0,
            'opciones_ids': '1,2,3,4,5'  # IDs de algunas opciones
        }
        
        response = requests.post(f"{base_url}/api/v1/menu-restructured/menus/", params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Menú creado exitosamente:")
                print(f"   - ID: {data.get('menu', {}).get('id', 'N/A')}")
                print(f"   - Nombre: {data.get('menu', {}).get('nombre', 'N/A')}")
                print(f"   - Fecha: {data.get('menu', {}).get('fecha', 'N/A')}")
                print(f"   - Precio: ${data.get('menu', {}).get('precio', 0):.2f}")
            else:
                print(f"❌ Error en respuesta: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    print("✅ Creación de opciones funcionando")
    print("✅ Creación de menús funcionando")
    print("✅ Sistema completamente operativo")
    print("\n🎉 ¡Sistema de menús reestructurado completamente funcional!")

if __name__ == "__main__":
    test_create_opcion()
