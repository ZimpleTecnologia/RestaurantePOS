#!/usr/bin/env python3
"""
Script para crear categorías básicas usando la API de la aplicación
"""
import requests
import json

def crear_categorias_via_api():
    """Crear categorías usando la API de la aplicación"""
    
    # URL base de la aplicación
    base_url = "http://localhost:8000"
    
    # Categorías básicas a crear
    categorias_basicas = [
        {"nombre": "Proteína", "descripcion": "Platos con proteína animal", "orden": 1},
        {"nombre": "Acompañamiento", "descripcion": "Arroces, papas, ensaladas", "orden": 2},
        {"nombre": "Principio", "descripcion": "Sopas y cremas", "orden": 3},
        {"nombre": "Bebida", "descripcion": "Jugos, gaseosas, agua", "orden": 4},
        {"nombre": "Postre", "descripcion": "Dulces y postres", "orden": 5}
    ]
    
    print("🔧 Creando categorías básicas via API...")
    
    for categoria_data in categorias_basicas:
        try:
            # URL del endpoint para crear categorías
            url = f"{base_url}/api/v1/restaurant-menu/categorias/"
            
            # Headers
            headers = {
                "Content-Type": "application/json"
            }
            
            # Hacer la petición POST
            response = requests.post(url, json=categoria_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                print(f"   ✅ Creada: {categoria_data['nombre']} (ID: {result.get('id', 'N/A')})")
            else:
                print(f"   ❌ Error creando {categoria_data['nombre']}: {response.status_code}")
                print(f"      Respuesta: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error de conexión: No se pudo conectar al servidor")
            print("💡 Asegúrate de que la aplicación esté ejecutándose en http://localhost:8000")
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return False
    
    print("🎉 Proceso completado")
    return True

def verificar_categorias():
    """Verificar que las categorías se crearon correctamente"""
    try:
        print("\n🔍 Verificando categorías creadas...")
        url = "http://localhost:8000/api/v1/restaurant-menu/categorias/"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            categorias = data.get('categorias', [])
            print(f"📊 Total de categorías: {len(categorias)}")
            
            for cat in categorias:
                print(f"   - {cat.get('nombre')} (ID: {cat.get('id')}, Activo: {cat.get('is_active')})")
        else:
            print(f"❌ Error verificando categorías: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando categorías: {e}")

if __name__ == "__main__":
    print("🏗️ CREADOR DE CATEGORÍAS VIA API")
    print("=" * 50)
    
    if crear_categorias_via_api():
        verificar_categorias()
