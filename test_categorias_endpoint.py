#!/usr/bin/env python3
"""
Script para probar el endpoint de categorías
"""
import requests
import json

def test_categorias_endpoint():
    """Probar el endpoint de categorías"""
    try:
        print("🔧 Probando endpoint de categorías...")
        
        # URL del endpoint
        url = "http://localhost:8000/api/v1/restaurant-menu/categorias/"
        
        # Hacer la petición
        response = requests.get(url)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📡 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Respuesta JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if 'categorias' in data:
                categorias = data['categorias']
                print(f"\n✅ Se encontraron {len(categorias)} categorías:")
                for cat in categorias:
                    print(f"   - ID: {cat.get('id')}, Nombre: {cat.get('nombre')}, Activo: {cat.get('is_active')}")
            else:
                print("❌ No se encontró la propiedad 'categorias' en la respuesta")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        print("💡 Asegúrate de que la aplicación esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_categorias_endpoint()
