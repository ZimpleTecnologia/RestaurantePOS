#!/usr/bin/env python3
"""
Script para probar los endpoints de imágenes
"""
import requests
import json

def test_image_endpoints():
    """Probar los endpoints de imágenes"""
    base_url = "http://localhost:8000"
    
    print("🖼️ Probando endpoints de imágenes...")
    
    # Probar endpoint de obtener imagen
    print("\n📸 Probando obtener imagen de opción...")
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/1/imagen")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Imagen obtenida correctamente")
        elif response.status_code == 404:
            print("   ℹ️ No hay imagen para esta opción")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   💥 Excepción: {str(e)}")
    
    # Probar endpoint de crear opción con imagen
    print("\n📤 Probando crear opción con imagen...")
    try:
        # Crear datos de prueba
        data = {
            'nombre': 'Plato de Prueba',
            'descripcion': 'Descripción de prueba',
            'tipo': 'Variable',
            'precio': 15000
        }
        
        # Crear archivo de prueba (simulado)
        files = {
            'imagen': ('test.jpg', b'fake_image_data', 'image/jpeg')
        }
        
        response = requests.post(
            f"{base_url}/api/v1/menu-restructured/opciones/with-image/",
            data=data,
            files=files
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Opción creada: {data.get('message', 'Sin mensaje')}")
            if 'opcion' in data:
                print(f"   📊 ID: {data['opcion'].get('id')}")
                print(f"   📊 Imagen URL: {data['opcion'].get('imagen_url', 'Sin imagen')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   💥 Excepción: {str(e)}")
    
    # Probar endpoint de actualizar opción con imagen
    print("\n🔄 Probando actualizar opción con imagen...")
    try:
        # Datos de actualización
        data = {
            'nombre': 'Plato Actualizado',
            'descripcion': 'Descripción actualizada',
            'precio': 18000
        }
        
        # Archivo de prueba
        files = {
            'imagen': ('test_updated.jpg', b'fake_updated_image_data', 'image/jpeg')
        }
        
        response = requests.put(
            f"{base_url}/api/v1/menu-restructured/opciones/1/with-image/",
            data=data,
            files=files
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Opción actualizada: {data.get('message', 'Sin mensaje')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   💥 Excepción: {str(e)}")

if __name__ == "__main__":
    test_image_endpoints()









