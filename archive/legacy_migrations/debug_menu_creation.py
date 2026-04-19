#!/usr/bin/env python3
"""
Script para diagnosticar el problema con la creación de menús
"""
import requests
import json

def debug_menu_creation():
    """Diagnosticar el problema con la creación de menús"""
    base_url = "http://localhost:8000"
    
    print("🔍 Diagnosticando creación de menús...")
    
    # Primero, verificar qué platos están disponibles
    print("\n📋 Verificando platos disponibles...")
    
    try:
        # Verificar platos fijos
        response = requests.get(f"{base_url}/api/v1/menu-restructured/platos-fijos/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Platos fijos disponibles: {data.get('total', 0)}")
            if data.get('platos'):
                for plato in data['platos'][:3]:  # Mostrar solo los primeros 3
                    print(f"   - {plato['nombre']} (ID: {plato['producto_id']})")
        else:
            print(f"❌ Error al obtener platos fijos: {response.status_code}")
            
        # Verificar platos variables
        response = requests.get(f"{base_url}/api/v1/menu-restructured/platos-variables/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Platos variables disponibles: {data.get('total', 0)}")
            if data.get('platos'):
                for plato in data['platos'][:3]:  # Mostrar solo los primeros 3
                    print(f"   - {plato['nombre']} (ID: {plato['producto_id']})")
        else:
            print(f"❌ Error al obtener platos variables: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Error al verificar platos: {str(e)}")
        return
    
    # Ahora probar la creación con datos más simples
    print("\n🍽️ Probando creación de menú con datos simples...")
    
    try:
        menu_data = {
            'fecha': '2025-09-22',  # Fecha diferente para evitar conflictos
            'nombre': 'Menú de Prueba Simple',
            'descripcion': 'Menú creado para diagnóstico',
            'precio': 14000,
            'platos_fijos_ids': '1',  # Solo un plato fijo
            'platos_variables_ids': '4'  # Solo un plato variable
        }
        
        print(f"📤 Enviando datos: {menu_data}")
        
        response = requests.post(
            f"{base_url}/api/v1/menu-restructured/menus/from-carta/",
            params=menu_data
        )
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Menú creado exitosamente")
                print(f"   ID: {data.get('menu', {}).get('id')}")
                print(f"   Opciones agregadas: {data.get('opciones_agregadas', 0)}")
            else:
                print(f"❌ Error en la respuesta: {data.get('message', 'Sin mensaje')}")
                print(f"   Error detallado: {data.get('error', 'Sin error')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"💥 Excepción al crear menú: {str(e)}")

if __name__ == "__main__":
    debug_menu_creation()










