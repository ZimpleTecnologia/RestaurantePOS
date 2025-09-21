#!/usr/bin/env python3
"""
Script para probar un endpoint específico y obtener detalles del error
"""
import requests
import json

def test_specific_endpoint():
    """Probar un endpoint específico para obtener detalles del error"""
    print("🔍 Probando endpoint específico para obtener detalles del error...")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de categorías con más detalles
    print("\n📋 Probando endpoint de categorías...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Content-Length: {response.headers.get('content-length', 'N/A')}")
        print(f"Raw Content: {response.text}")
        
        if response.status_code == 500:
            print("\n❌ Error 500 - Revisando posibles causas:")
            print("1. Error en la base de datos")
            print("2. Error en las relaciones SQLAlchemy")
            print("3. Error en el router o schemas")
            print("4. Error en la configuración")
            
            # Intentar obtener más información del error
            try:
                error_data = response.json()
                print(f"Error JSON: {error_data}")
            except:
                print("No se pudo parsear el error como JSON")
                
    except requests.exceptions.Timeout:
        print("❌ Timeout - El servidor no responde")
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - El servidor no está ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    # Probar endpoint de documentación para ver si el router está registrado
    print("\n📚 Verificando si el router está registrado en la documentación...")
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            restaurant_menu_paths = [path for path in paths.keys() if 'restaurant-menu' in path]
            
            if restaurant_menu_paths:
                print(f"✅ Router restaurant-menu registrado con {len(restaurant_menu_paths)} endpoints:")
                for path in restaurant_menu_paths:
                    print(f"   - {path}")
            else:
                print("❌ Router restaurant-menu no está registrado en la documentación")
                print("💡 Verifica que el router esté incluido en main.py")
        else:
            print(f"❌ Error obteniendo documentación: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verificando documentación: {e}")

if __name__ == "__main__":
    test_specific_endpoint()


