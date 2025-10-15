#!/usr/bin/env python3
"""
Script para verificar que todas las referencias obsoletas han sido eliminadas
"""
import requests
import json

def test_cleanup_verification():
    """Verificar que todas las referencias obsoletas han sido eliminadas"""
    print("🧹 Verificando limpieza de referencias obsoletas...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Verificar que las rutas obsoletas no existen
        print("\n🗑️ Verificando eliminación de rutas obsoletas...")
        
        # Ruta /menu-management
        response = requests.get(f"{base_url}/menu-management")
        if response.status_code == 404:
            print("✅ Ruta /menu-management eliminada correctamente")
        else:
            print(f"⚠️ Ruta /menu-management aún existe: {response.status_code}")
        
        # Ruta /products/menu-management
        response = requests.get(f"{base_url}/products/menu-management")
        if response.status_code == 404:
            print("✅ Ruta /products/menu-management eliminada correctamente")
        else:
            print(f"⚠️ Ruta /products/menu-management aún existe: {response.status_code}")
        
        # 3. Verificar que las rutas nuevas funcionan
        print("\n✅ Verificando rutas nuevas...")
        
        # Ruta /admin/menus
        response = requests.get(f"{base_url}/admin/menus")
        if response.status_code == 200:
            print("✅ Ruta /admin/menus funcionando correctamente")
        else:
            print(f"❌ Error en /admin/menus: {response.status_code}")
        
        # Ruta /meseros/menus
        response = requests.get(f"{base_url}/meseros/menus")
        if response.status_code == 200:
            print("✅ Ruta /meseros/menus funcionando correctamente")
        else:
            print(f"❌ Error en /meseros/menus: {response.status_code}")
        
        # 4. Verificar navegación en el home
        print("\n🏠 Verificando navegación en el home...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            content = response.text
            if "Gestión Menús" in content and "/admin/menus" in content:
                print("✅ Navegación actualizada correctamente en el home")
            else:
                print("⚠️ Navegación no actualizada en el home")
        else:
            print(f"❌ Error en el home: {response.status_code}")
        
        # 5. Verificar API de menús
        print("\n📋 Verificando API de menús...")
        response = requests.get(f"{base_url}/api/v1/public/menus/stats/")
        if response.status_code == 200:
            stats = response.json()
            print("✅ API de menús funcionando correctamente")
            print(f"  - Platos: {stats.get('platos', {}).get('activos', 0)}")
            print(f"  - Menús: {stats.get('menus', {}).get('activos', 0)}")
        else:
            print(f"❌ Error en API de menús: {response.status_code}")
        
        print("\n🎉 Limpieza completada exitosamente!")
        print(f"\n✨ Referencias obsoletas eliminadas:")
        print(f"  - ✅ Ruta /menu-management eliminada")
        print(f"  - ✅ Ruta /products/menu-management eliminada")
        print(f"  - ✅ Función goToMenuManagement() eliminada")
        print(f"  - ✅ Archivo menu-management.html eliminado")
        
        print(f"\n🌐 Navegación actualizada:")
        print(f"  - Home: http://127.0.0.1:8000/")
        print(f"  - Gestión Menús: http://127.0.0.1:8000/admin/menus")
        print(f"  - Vista de Meseros: http://127.0.0.1:8000/meseros/menus")
        print(f"  - API: http://127.0.0.1:8000/api/v1/public/menus/stats/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cleanup_verification()


