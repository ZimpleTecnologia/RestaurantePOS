#!/usr/bin/env python3
"""
Script para probar los endpoints del sistema de menús
"""

import requests
import json

def test_endpoints():
    """Probar los endpoints del sistema de menús"""
    base_url = "http://localhost:8000/api/v1/menu-restructured"
    
    print("🧪 Probando Endpoints del Sistema de Menús")
    print("=" * 50)
    
    # 1. Probar endpoint de platos fijos
    print("\n1. 🍽️  Probando endpoint de platos fijos...")
    try:
        response = requests.get(f"{base_url}/platos-fijos/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total platos: {data.get('total', 0)}")
            print(f"   🔍 Success: {data.get('success', False)}")
            
            if data.get('platos'):
                print("   📋 Primeros 3 platos:")
                for plato in data['platos'][:3]:
                    print(f"      - {plato['nombre']} (${plato['precio_base']:,.0f} COP)")
            else:
                print("   ⚠️  No hay platos fijos disponibles")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 2. Probar endpoint de platos variables
    print("\n2. 🔄 Probando endpoint de platos variables...")
    try:
        response = requests.get(f"{base_url}/platos-variables/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total platos: {data.get('total', 0)}")
            print(f"   🔍 Success: {data.get('success', False)}")
            
            if data.get('platos'):
                print("   📋 Primeros 3 platos:")
                for plato in data['platos'][:3]:
                    print(f"      - {plato['nombre']} (${plato['precio_base']:,.0f} COP)")
            else:
                print("   ⚠️  No hay platos variables disponibles")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 3. Probar endpoint de categorías
    print("\n3. 🏷️  Probando endpoint de categorías...")
    try:
        response = requests.get(f"{base_url}/categorias/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total categorías: {data.get('total', 0)}")
            print(f"   🔍 Success: {data.get('success', False)}")
            
            if data.get('categorias'):
                print("   📋 Categorías disponibles:")
                for cat in data['categorias']:
                    print(f"      - {cat['nombre']}")
            else:
                print("   ⚠️  No hay categorías disponibles")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 4. Probar endpoint de opciones
    print("\n4. ⚙️  Probando endpoint de opciones...")
    try:
        response = requests.get(f"{base_url}/opciones/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total opciones: {data.get('total', 0)}")
            print(f"   🔍 Success: {data.get('success', False)}")
            
            if data.get('opciones'):
                print("   📋 Primeras 3 opciones:")
                for opcion in data['opciones'][:3]:
                    print(f"      - {opcion['nombre']} ({opcion['tipo']}) - ${opcion['precio']:,.0f} COP")
            else:
                print("   ⚠️  No hay opciones disponibles")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    # 5. Probar endpoint de estadísticas
    print("\n5. 📊 Probando endpoint de estadísticas...")
    try:
        response = requests.get(f"{base_url}/stats/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   🔍 Success: {data.get('success', False)}")
            
            if data.get('stats'):
                stats = data['stats']
                print("   📈 Estadísticas del sistema:")
                print(f"      - Categorías: {stats.get('categorias', 0)}")
                print(f"      - Opciones: {stats.get('opciones', 0)}")
                print(f"      - Menús: {stats.get('menus', 0)}")
                print(f"      - Platos fijos: {stats.get('platos_fijos', 0)}")
                print(f"      - Platos variables: {stats.get('platos_variables', 0)}")
            else:
                print("   ⚠️  No hay estadísticas disponibles")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Pruebas de endpoints completadas")

if __name__ == "__main__":
    test_endpoints()
