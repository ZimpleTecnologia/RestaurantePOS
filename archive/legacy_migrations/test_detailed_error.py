#!/usr/bin/env python3
"""
Script para obtener detalles del error 500
"""
import requests
import json

def test_detailed_error():
    """Obtener detalles del error 500"""
    print("🔍 Obteniendo detalles del error 500...")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Probar endpoint de categorías con más detalles
    print("\n📋 Probando endpoint de categorías con detalles...")
    try:
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text}")
        
        if response.status_code == 500:
            print("\n❌ Error 500 detectado")
            print("Posibles causas:")
            print("1. Error en la base de datos (tabla no existe)")
            print("2. Error en las relaciones de SQLAlchemy")
            print("3. Error en el router o schemas")
            print("4. Error en la configuración de la base de datos")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Probar endpoint de documentación para ver si el router está registrado
    print("\n📚 Verificando documentación de la API...")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Documentación disponible")
            print("Revisa http://127.0.0.1:8000/docs para ver los endpoints disponibles")
        else:
            print("❌ Documentación no disponible")
    except Exception as e:
        print(f"❌ Error accediendo a documentación: {e}")
    
    # Probar endpoint de salud
    print("\n🏥 Verificando endpoint de salud...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Servidor funcionando")
            print(f"Response: {response.json()}")
        else:
            print("❌ Endpoint de salud no disponible")
    except Exception as e:
        print(f"❌ Error en endpoint de salud: {e}")

if __name__ == "__main__":
    test_detailed_error()


