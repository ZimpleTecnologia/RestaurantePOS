#!/usr/bin/env python3
"""
Script de prueba para verificar el endpoint DELETE de opciones con desactivación automática
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
OPCION_ID = 45  # ID de la opción que se intenta eliminar

def test_delete_opcion():
    """Probar el endpoint DELETE para opciones"""
    url = f"{BASE_URL}/api/v1/menu-restructured/opciones/{OPCION_ID}"
    
    print(f"🧪 Probando DELETE: {url}")
    
    try:
        # Realizar la petición DELETE
        response = requests.delete(url)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            action = data.get("action", "unknown")
            
            if action == "deleted":
                print("✅ ÉXITO: Opción eliminada permanentemente")
                print(f"📄 Mensaje: {data.get('message')}")
            
            elif action == "deactivated":
                print("⚠️ DESACTIVADA: La opción ha sido desactivada")
                print(f"📄 Mensaje: {data.get('message')}")
                print(f"⚠️ Advertencia: {data.get('warning')}")
                print(f"📊 Menús afectados: {data.get('menu_count')}")
                opcion_info = data.get('opcion', {})
                print(f"🍽️ Estado actual: {opcion_info}")
            
            elif action == "already_inactive":
                print("ℹ️ INFO: La opción ya estaba desactivada")
                print(f"📄 Mensaje: {data.get('message')}")
                print(f"⚠️ Advertencia: {data.get('warning')}")
                print(f"📊 Menús afectados: {data.get('menu_count')}")
            
            print(f"\n📋 Respuesta completa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        elif response.status_code == 404:
            print("❌ ERROR 404: Opción no encontrada")
            print(f"📄 Respuesta: {response.text}")
        elif response.status_code == 400:
            print("⚠️ ERROR 400: No se puede eliminar")
            print(f"📄 Respuesta: {response.text}")
        elif response.status_code == 405:
            print("❌ ERROR 405: Método no permitido - El endpoint no existe")
            print(f"📄 Respuesta: {response.text}")
        else:
            print(f"❓ ERROR {response.status_code}: Respuesta inesperada")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor")
        print("💡 Asegúrate de que la aplicación esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")

def test_get_opcion():
    """Verificar si la opción existe antes de eliminarla"""
    url = f"{BASE_URL}/api/v1/menu-restructured/opciones/"
    
    print(f"\n🔍 Verificando opciones disponibles...")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            opciones = response.json()
            print(f"📋 Total de opciones: {len(opciones.get('opciones', []))}")
            
            # Buscar la opción específica
            for opcion in opciones.get('opciones', []):
                if opcion.get('id') == OPCION_ID:
                    print(f"✅ Opción {OPCION_ID} encontrada: {opcion.get('nombre')}")
                    return True
            
            print(f"❌ Opción {OPCION_ID} no encontrada en la lista")
            return False
        else:
            print(f"❌ Error al obtener opciones: {response.status_code}")
            return False
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando prueba del endpoint DELETE para opciones")
    print("=" * 60)
    
    # Verificar si la opción existe
    if test_get_opcion():
        print(f"\n🗑️ Intentando eliminar opción ID: {OPCION_ID}")
        test_delete_opcion()
    else:
        print(f"\n⚠️ No se puede probar la eliminación - Opción {OPCION_ID} no existe")
    
    print("\n" + "=" * 60)
    print("🏁 Prueba completada")
