#!/usr/bin/env python3
"""
Script para probar los endpoints del módulo de menús reestructurado
"""
import requests
import json
from datetime import datetime

def test_menu_endpoints():
    """Probar todos los endpoints del módulo de menús"""
    base_url = "http://localhost:8000"
    
    print("🧪 Probando endpoints del módulo de menús...")
    
    # Lista de endpoints a probar
    endpoints = [
        "/api/v1/menu-restructured/",
        "/api/v1/menu-restructured/stats/",
        "/api/v1/menu-restructured/menus/",
        "/api/v1/menu-restructured/categorias/",
        "/api/v1/menu-restructured/opciones/",
        "/api/v1/menu-restructured/platos-fijos/",
        "/api/v1/menu-restructured/platos-variables/"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Probando: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Éxito: {data.get('message', 'Sin mensaje')}")
                if 'stats' in data:
                    print(f"   📊 Stats: {data['stats']}")
                elif 'total' in data:
                    print(f"   📊 Total: {data['total']}")
                results[endpoint] = "✅ OK"
            else:
                print(f"   ❌ Error: {response.text}")
                results[endpoint] = f"❌ {response.status_code}"
                
        except Exception as e:
            print(f"   💥 Excepción: {str(e)}")
            results[endpoint] = f"💥 {str(e)}"
    
    # Resumen
    print("\n" + "="*50)
    print("📋 RESUMEN DE PRUEBAS")
    print("="*50)
    
    for endpoint, result in results.items():
        print(f"{endpoint}: {result}")
    
    # Probar creación de menú
    print("\n🍽️ Probando creación de menú...")
    try:
        menu_data = {
            'fecha': '2025-09-21',
            'nombre': 'Menú de Prueba',
            'descripcion': 'Menú creado desde script de prueba',
            'precio': 14000,
            'platos_fijos_ids': '1,2,3',
            'platos_variables_ids': '4,5,6'
        }
        
        response = requests.post(
            f"{base_url}/api/v1/menu-restructured/menus/from-carta/",
            params=menu_data
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Menú creado: {data.get('message', 'Sin mensaje')}")
            if 'opciones_agregadas' in data:
                print(f"   📊 Opciones agregadas: {data['opciones_agregadas']}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   💥 Excepción: {str(e)}")

if __name__ == "__main__":
    test_menu_endpoints()









