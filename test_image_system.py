#!/usr/bin/env python3
"""
Script para probar el sistema de imágenes en BD
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_image_system():
    """Probar el sistema completo de imágenes"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔄 Probando sistema de imágenes...")
    
    # 1. Verificar que el servidor esté funcionando
    try:
        response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/")
        if response.status_code == 200:
            print("✅ Servidor funcionando")
            data = response.json()
            print(f"📊 Total de opciones: {data.get('total', 0)}")
            
            # Mostrar información de cada opción
            for opcion in data.get('opciones', []):
                print(f"\n🍽️  Opción: {opcion['nombre']}")
                print(f"   - ID: {opcion['id']}")
                print(f"   - Tipo: {opcion['tipo']}")
                print(f"   - Precio: ${opcion['precio']}")
                print(f"   - Tiene imagen_data: {opcion.get('imagen_data', False)}")
                print(f"   - Tipo de imagen: {opcion.get('imagen_tipo', 'N/A')}")
                print(f"   - URL de imagen: {opcion.get('imagen_url', 'N/A')}")
                
                # Probar endpoint de imagen
                if opcion.get('imagen_data'):
                    try:
                        img_response = requests.get(f"{base_url}/api/v1/menu-restructured/opciones/{opcion['id']}/imagen")
                        if img_response.status_code == 200:
                            print(f"   ✅ Imagen accesible (tamaño: {len(img_response.content)} bytes)")
                        else:
                            print(f"   ❌ Error accediendo imagen: {img_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Error probando imagen: {e}")
                else:
                    print(f"   ⚠️  No tiene imagen")
        else:
            print(f"❌ Error del servidor: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está ejecutándose?")
        print("Ejecuta: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_image_system()
