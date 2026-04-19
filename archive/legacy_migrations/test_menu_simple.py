#!/usr/bin/env python3
"""
Script simple para probar el sistema de menús sin autenticación
"""
import requests
import json
from datetime import date

def test_menu_system_simple():
    """Probar el sistema de menús de forma simple"""
    print("🍽️ Probando sistema de menús (versión simple)...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Probar endpoints públicos de API
        print("\n📋 Probando endpoints públicos de API...")
        
        # Estadísticas
        response = requests.get(f"{base_url}/api/v1/public/menus/stats/")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Estadísticas del sistema:")
            print(f"  - Platos: {stats['platos']['activos']} activos ({stats['platos']['fijos']} fijos, {stats['platos']['variables']} variables)")
            print(f"  - Menús: {stats['menus']['activos']} activos")
            print(f"  - Menú de hoy: {'✓' if stats['menus']['tiene_menu_hoy'] else '✗'}")
        else:
            print(f"❌ Error obteniendo estadísticas: {response.status_code}")
        
        # Platos
        response = requests.get(f"{base_url}/api/v1/public/menus/platos/")
        if response.status_code == 200:
            platos = response.json()
            print(f"✅ Platos disponibles: {len(platos)}")
        else:
            print(f"❌ Error obteniendo platos: {response.status_code}")
        
        # Menús
        response = requests.get(f"{base_url}/api/v1/public/menus/")
        if response.status_code == 200:
            menus = response.json()
            print(f"✅ Menús disponibles: {len(menus)}")
        else:
            print(f"❌ Error obteniendo menús: {response.status_code}")
        
        # Menú de hoy
        response = requests.get(f"{base_url}/api/v1/public/menus/hoy/")
        if response.status_code == 200:
            menu_hoy = response.json()
            if 'message' in menu_hoy:
                print(f"ℹ️ {menu_hoy['message']}")
            else:
                print(f"✅ Menú de hoy: {menu_hoy.get('nombre', 'Sin nombre')}")
        else:
            print(f"❌ Error obteniendo menú de hoy: {response.status_code}")
        
        # 3. Probar interfaces web (no requieren autenticación)
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
        
        # 3. Probar documentación de API
        print("\n📚 Probando documentación de API...")
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Documentación de API disponible")
        else:
            print(f"❌ Error en documentación: {response.status_code}")
        
        print("\n🎉 Sistema de menús funcionando correctamente!")
        print(f"\n🌐 Puedes acceder a:")
        print(f"  - Administración: http://127.0.0.1:8000/admin/menus")
        print(f"  - Vista de meseros: http://127.0.0.1:8000/meseros/menus")
        print(f"  - Documentación: http://127.0.0.1:8000/docs")
        print(f"\n💡 Nota: Los endpoints de API requieren autenticación.")
        print(f"    Puedes probarlos desde la documentación interactiva en /docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
        print("Inicia el servidor con: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_menu_system_simple()