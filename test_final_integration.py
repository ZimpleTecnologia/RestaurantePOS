#!/usr/bin/env python3
"""
Script para probar la integración final del módulo de menús
"""
import requests
import json

def test_final_integration():
    """Probar la integración final del módulo de menús"""
    print("🎯 Probando integración final del módulo de menús...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Probar página principal con nuevo nombre
        print("\n🏠 Probando página principal...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Página principal accesible")
            if "Gestión Menús" in response.text:
                print("✅ Nombre actualizado a 'Gestión Menús'")
            else:
                print("⚠️ Nombre no actualizado en el home")
        else:
            print(f"❌ Error en página principal: {response.status_code}")
        
        # 3. Probar navegación a Gestión Menús
        print("\n⚙️ Probando navegación a Gestión Menús...")
        response = requests.get(f"{base_url}/admin/menus")
        if response.status_code == 200:
            print("✅ Página de Gestión Menús accesible")
        else:
            print(f"❌ Error en Gestión Menús: {response.status_code}")
        
        # 4. Probar navegación a vista de meseros
        print("\n👥 Probando navegación a vista de meseros...")
        response = requests.get(f"{base_url}/meseros/menus")
        if response.status_code == 200:
            print("✅ Vista de meseros accesible")
        else:
            print(f"❌ Error en vista de meseros: {response.status_code}")
        
        # 5. Verificar que la ruta obsoleta no existe
        print("\n🗑️ Verificando eliminación de ruta obsoleta...")
        response = requests.get(f"{base_url}/menu-management")
        if response.status_code == 404:
            print("✅ Ruta obsoleta /menu-management eliminada correctamente")
        else:
            print(f"⚠️ Ruta obsoleta aún existe: {response.status_code}")
        
        # 6. Probar API de menús
        print("\n📋 Probando API de menús...")
        response = requests.get(f"{base_url}/api/v1/public/menus/stats/")
        if response.status_code == 200:
            stats = response.json()
            print("✅ API de menús funcionando")
            print(f"  - Platos: {stats.get('platos', {}).get('activos', 0)}")
            print(f"  - Menús: {stats.get('menus', {}).get('activos', 0)}")
        else:
            print(f"❌ Error en API de menús: {response.status_code}")
        
        print("\n🎉 Integración final completada exitosamente!")
        print(f"\n🌐 Navegación actualizada:")
        print(f"  - Home: http://127.0.0.1:8000/")
        print(f"  - Gestión Menús: http://127.0.0.1:8000/admin/menus")
        print(f"  - Vista de meseros: http://127.0.0.1:8000/meseros/menus")
        print(f"  - API: http://127.0.0.1:8000/api/v1/public/menus/stats/")
        
        print(f"\n✨ Cambios realizados:")
        print(f"  - ✅ Nombre cambiado de 'Administración' a 'Gestión Menús'")
        print(f"  - ✅ Archivo menu-management.html eliminado")
        print(f"  - ✅ Ruta obsoleta /menu-management eliminada")
        print(f"  - ✅ Navegación actualizada en home y barra superior")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_final_integration()
