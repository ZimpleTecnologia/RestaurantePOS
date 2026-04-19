#!/usr/bin/env python3
"""
Script para probar los endpoints del sistema de menús del restaurante
"""
import requests
import json

def test_menu_endpoints():
    """Probar los endpoints del sistema de menús del restaurante"""
    print("🍽️ Probando Endpoints del Sistema de Menús del Restaurante...")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor funcionando")
            else:
                print(f"⚠️ Servidor respondió con código: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Servidor no está ejecutándose")
            print("Inicia el servidor con: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # 2. Probar categorías
        print("\n📋 Probando categorías...")
        try:
            response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Categorías obtenidas: {data.get('total', 0)}")
                for categoria in data.get('categorias', []):
                    print(f"   - {categoria.get('nombre', 'N/A')}: {categoria.get('descripcion', 'Sin descripcion')}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error probando categorías: {e}")
        
        # 3. Probar platos
        print("\n🍽️ Probando platos...")
        try:
            response = requests.get(f"{base_url}/api/v1/restaurant-menu/platos/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Platos obtenidos: {data.get('total', 0)}")
                for plato in data.get('platos', [])[:5]:  # Mostrar solo los primeros 5
                    print(f"   - {plato.get('nombre', 'N/A')}: ${plato.get('precio', 0)} ({plato.get('tipo', 'N/A')})")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error probando platos: {e}")
        
        # 4. Probar acompañamientos fijos
        print("\n🥗 Probando acompañamientos fijos...")
        try:
            response = requests.get(f"{base_url}/api/v1/restaurant-menu/acompanamientos/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Acompañamientos obtenidos: {data.get('total', 0)}")
                for acompanamiento in data.get('acompanamientos', []):
                    print(f"   - {acompanamiento.get('nombre', 'N/A')}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error probando acompañamientos: {e}")
        
        # 5. Probar menús del día
        print("\n📅 Probando menús del día...")
        try:
            response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Menús obtenidos: {data.get('total', 0)}")
                for menu in data.get('menus', []):
                    print(f"   - {menu.get('nombre', 'N/A')} ({menu.get('fecha', 'N/A')}) - Publicado: {menu.get('publicado', False)}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error probando menús: {e}")
        
        # 6. Probar menú de hoy
        print("\n📅 Probando menú de hoy...")
        try:
            response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/hoy")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Menú de hoy obtenido: {data.get('menu', {}).get('nombre', 'N/A')}")
                print(f"   Categorías disponibles: {list(data.get('categorias', {}).keys())}")
                print(f"   Acompañamientos fijos: {len(data.get('acompanamientos_fijos', []))}")
                print(f"   Platos fijos: {len(data.get('platos_fijos', []))}")
            elif response.status_code == 404:
                print("⚠️ No hay menú publicado para hoy")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error probando menú de hoy: {e}")
        
        print("\n" + "=" * 70)
        print("🎉 Pruebas de endpoints completadas!")
        print("\n📋 Endpoints probados:")
        print("  - ✅ GET /api/v1/restaurant-menu/categorias/")
        print("  - ✅ GET /api/v1/restaurant-menu/platos/")
        print("  - ✅ GET /api/v1/restaurant-menu/acompanamientos/")
        print("  - ✅ GET /api/v1/restaurant-menu/menus/")
        print("  - ✅ GET /api/v1/restaurant-menu/menus/hoy")
        
        print("\n🌐 URLs del sistema:")
        print("  - Home: http://127.0.0.1:8000/")
        print("  - Gestión de Menús: http://127.0.0.1:8000/admin/menus")
        print("  - Vista de Meseros: http://127.0.0.1:8000/meseros/menus")
        print("  - Documentación API: http://127.0.0.1:8000/docs")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_menu_endpoints()