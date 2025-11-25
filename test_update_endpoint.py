#!/usr/bin/env python3
"""
Script para probar el endpoint de actualización de menús
"""
import requests
import json

def test_update_menu():
    """Probar el endpoint de actualización de menús"""
    base_url = "http://localhost:8000"
    
    # Datos de prueba
    menu_id = 5
    update_data = {
        "fecha": "2025-09-22",
        "nombre": "Menú Ejecutivo (Actualizado)",
        "descripcion": "Menú actualizado para prueba",
        "precio": 15000,
        "platos_fijos_ids": "1,2,3",
        "platos_variables_ids": "7,8"
    }
    
    try:
        print(f"🔄 Probando actualización del menú ID: {menu_id}")
        print(f"📊 Datos: {json.dumps(update_data, indent=2)}")
        
        # Construir URL con parámetros
        params = []
        for key, value in update_data.items():
            params.append(f"{key}={value}")
        
        url = f"{base_url}/api/v1/menu-restructured/menus/{menu_id}/?{'&'.join(params)}"
        print(f"🌐 URL: {url}")
        
        # Realizar petición PUT
        response = requests.put(url, timeout=10)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Error en la respuesta:")
            print(f"   Status: {response.status_code}")
            print(f"   Content: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_update_menu()
    if success:
        print("\n🎉 La actualización de menús funciona correctamente")
    else:
        print("\n💥 Hay problemas con la actualización de menús")










