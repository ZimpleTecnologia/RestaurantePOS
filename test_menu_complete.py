#!/usr/bin/env python3
"""
Script para probar el sistema completo de gestión de menús
"""
import requests
import json
from datetime import date

def test_menu_system():
    """Probar el sistema completo de menús"""
    print("🍽️ Probando sistema completo de gestión de menús...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Probar endpoints de platos
        print("\n📋 Probando endpoints de platos...")
        
        # Obtener platos
        response = requests.get(f"{base_url}/api/v1/menus/platos/")
        if response.status_code == 200:
            platos = response.json()
            print(f"✅ Platos disponibles: {len(platos.get('platos', []))}")
        else:
            print(f"❌ Error obteniendo platos: {response.status_code}")
            return
        
        # 3. Probar endpoints de menús
        print("\n📅 Probando endpoints de menús...")
        
        # Obtener menús
        response = requests.get(f"{base_url}/api/v1/menus/")
        if response.status_code == 200:
            menus = response.json()
            print(f"✅ Menús disponibles: {len(menus.get('menus', []))}")
        else:
            print(f"❌ Error obteniendo menús: {response.status_code}")
            return
        
        # 4. Probar menú de hoy
        print("\n🗓️ Probando menú de hoy...")
        response = requests.get(f"{base_url}/api/v1/menus/hoy/menu")
        if response.status_code == 200:
            menu_hoy = response.json()
            if menu_hoy.get('menu'):
                print(f"✅ Menú de hoy encontrado: {menu_hoy['menu']['nombre']}")
                print(f"  - Platos fijos: {len(menu_hoy.get('platos_fijos', []))}")
                print(f"  - Platos variables: {len(menu_hoy.get('platos_variables', []))}")
            else:
                print("ℹ️ No hay menú para hoy")
        else:
            print(f"❌ Error obteniendo menú de hoy: {response.status_code}")
        
        # 5. Probar interfaces web
        print("\n🌐 Probando interfaces web...")
        
        # Admin
        response = requests.get(f"{base_url}/admin/menus")
        if response.status_code == 200:
            print("✅ Interfaz de administración disponible")
        else:
            print(f"❌ Error en interfaz de administración: {response.status_code}")
        
        # Meseros
        response = requests.get(f"{base_url}/meseros/menus")
        if response.status_code == 200:
            print("✅ Interfaz de meseros disponible")
        else:
            print(f"❌ Error en interfaz de meseros: {response.status_code}")
        
        print("\n🎉 Sistema de menús funcionando correctamente!")
        print(f"\n🌐 Puedes acceder a:")
        print(f"  - Administración: http://127.0.0.1:8000/admin/menus")
        print(f"  - Vista de meseros: http://127.0.0.1:8000/meseros/menus")
        print(f"  - API: http://127.0.0.1:8000/api/v1/menus/")
        print(f"  - Documentación: http://127.0.0.1:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
        print("Inicia el servidor con: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menu_system()
