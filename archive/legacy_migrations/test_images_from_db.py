#!/usr/bin/env python3
"""
Script para probar que las imágenes se carguen correctamente desde la BD
"""
import requests
import json

def test_images_from_db():
    """Probar que las imágenes se carguen desde la BD"""
    base_url = "http://localhost:8000"
    
    print("🖼️ Probando carga de imágenes desde BD...")
    
    # Probar endpoint de opciones
    print("\n📋 Probando endpoint de opciones...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Opciones cargadas: {data.get('total', 0)}")
            
            if data.get('opciones'):
                for opcion in data['opciones'][:3]:  # Mostrar solo las primeras 3
                    print(f"   📊 {opcion['nombre']}:")
                    print(f"      - Tiene imagen: {opcion.get('tiene_imagen', False)}")
                    print(f"      - Imagen data: {opcion.get('imagen_data', False)}")
                    
                    # Probar endpoint de imagen si tiene imagen
                    if opcion.get('tiene_imagen') or opcion.get('imagen_data'):
                        print(f"      - Probando imagen...")
                        img_response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/{opcion['id']}/imagen")
                        print(f"      - Status imagen: {img_response.status_code}")
                        if img_response.status_code == 200:
                            print(f"      - ✅ Imagen obtenida correctamente")
                        else:
                            print(f"      - ❌ Error al obtener imagen: {img_response.text}")
                    else:
                        print(f"      - ℹ️ No tiene imagen")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   💥 Excepción: {str(e)}")
    
    # Probar endpoint específico de imagen
    print("\n🖼️ Probando endpoint de imagen específico...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/1/imagen")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Imagen obtenida correctamente")
            print(f"   📊 Tamaño: {len(response.content)} bytes")
            print(f"   📊 Content-Type: {response.headers.get('content-type', 'No especificado')}")
        elif response.status_code == 404:
            print(f"   ℹ️ No hay imagen para esta opción")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   💥 Excepción: {str(e)}")

if __name__ == "__main__":
    test_images_from_db()










