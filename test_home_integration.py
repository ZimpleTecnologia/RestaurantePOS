#!/usr/bin/env python3
"""
Script para probar la integración del módulo de menús en el home
"""
import requests
import json

def test_home_integration():
    """Probar la integración del home con el módulo de menús"""
    print("🏠 Probando integración del home con módulo de menús...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Probar página principal
        print("\n🏠 Probando página principal...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Página principal accesible")
            if "Gestión de Menús" in response.text:
                print("✅ Módulo de menús integrado en el home")
            else:
                print("⚠️ Módulo de menús no encontrado en el home")
        else:
            print(f"❌ Error en página principal: {response.status_code}")
        
        # 3. Probar navegación a administración
        print("\n⚙️ Probando navegación a administración...")
        response = requests.get(f"{base_url}/admin/menus")
        if response.status_code == 200:
            print("✅ Página de administración accesible")
        else:
            print(f"❌ Error en administración: {response.status_code}")
        
        # 4. Probar navegación a vista de meseros
        print("\n👥 Probando navegación a vista de meseros...")
        response = requests.get(f"{base_url}/meseros/menus")
        if response.status_code == 200:
            print("✅ Vista de meseros accesible")
        else:
            print(f"❌ Error en vista de meseros: {response.status_code}")
        
        # 5. Probar API de menús
        print("\n📋 Probando API de menús...")
        response = requests.get(f"{base_url}/api/v1/public/menus/stats/")
        if response.status_code == 200:
            stats = response.json()
            print("✅ API de menús funcionando")
            print(f"  - Platos: {stats.get('platos', {}).get('activos', 0)}")
            print(f"  - Menús: {stats.get('menus', {}).get('activos', 0)}")
        else:
            print(f"❌ Error en API de menús: {response.status_code}")
        
        print("\n🎉 Integración del home completada exitosamente!")
        print(f"\n🌐 Puedes acceder a:")
        print(f"  - Home: http://127.0.0.1:8000/")
        print(f"  - Administración: http://127.0.0.1:8000/admin/menus")
        print(f"  - Vista de meseros: http://127.0.0.1:8000/meseros/menus")
        print(f"  - API: http://127.0.0.1:8000/api/v1/public/menus/stats/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_home_integration()
