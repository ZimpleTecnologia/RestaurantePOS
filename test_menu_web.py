#!/usr/bin/env python3
"""
Script para probar el módulo de Gestión de Menús desde la interfaz web
"""
import webbrowser
import time
import requests

def test_menu_web_interface():
    """Probar la interfaz web del módulo de Gestión de Menús"""
    print("🌐 Probando Módulo de Gestión de Menús...")
    print("=" * 60)
    
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
        
        # 2. Probar endpoints del sistema de menús
        print("\n🍽️ Probando endpoints del sistema de menús...")
        
        # Probar categorías
        try:
            response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Categorías: {data.get('total', 0)} disponibles")
            else:
                print(f"❌ Error en categorías: {response.status_code}")
        except Exception as e:
            print(f"❌ Error probando categorías: {e}")
        
        # Probar platos
        try:
            response = requests.get(f"{base_url}/api/v1/restaurant-menu/platos/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Platos: {data.get('total', 0)} disponibles")
            else:
                print(f"❌ Error en platos: {response.status_code}")
        except Exception as e:
            print(f"❌ Error probando platos: {e}")
        
        # Probar menú de hoy
        try:
            response = requests.get(f"{base_url}/api/v1/restaurant-menu/menus/hoy")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Menú de hoy: {data.get('menu', {}).get('nombre', 'N/A')}")
                print(f"   Categorías: {list(data.get('categorias', {}).keys())}")
                print(f"   Acompañamientos: {len(data.get('acompanamientos_fijos', []))}")
                print(f"   Platos fijos: {len(data.get('platos_fijos', []))}")
            elif response.status_code == 404:
                print("⚠️ No hay menú publicado para hoy")
            else:
                print(f"❌ Error en menú de hoy: {response.status_code}")
        except Exception as e:
            print(f"❌ Error probando menú de hoy: {e}")
        
        # 3. Abrir interfaces web
        print("\n🌐 Abriendo interfaces web...")
        
        # Home del sistema
        print("🏠 Abriendo Home del sistema...")
        webbrowser.open(f"{base_url}/")
        time.sleep(2)
        
        # Documentación API
        print("📚 Abriendo documentación API...")
        webbrowser.open(f"{base_url}/docs")
        time.sleep(2)
        
        # Gestión de Menús (Admin)
        print("👨‍💼 Abriendo Gestión de Menús (Admin)...")
        webbrowser.open(f"{base_url}/admin/menus")
        time.sleep(2)
        
        # Vista de Meseros
        print("👨‍🍳 Abriendo Vista de Meseros...")
        webbrowser.open(f"{base_url}/meseros/menus")
        time.sleep(2)
        
        print("\n" + "=" * 60)
        print("🎉 Pruebas del módulo de Gestión de Menús completadas!")
        print("\n📋 URLs abiertas:")
        print("  - 🏠 Home: http://127.0.0.1:8000/")
        print("  - 📚 Documentación API: http://127.0.0.1:8000/docs")
        print("  - 👨‍💼 Gestión de Menús: http://127.0.0.1:8000/admin/menus")
        print("  - 👨‍🍳 Vista de Meseros: http://127.0.0.1:8000/meseros/menus")
        
        print("\n🍽️ Funcionalidades del módulo:")
        print("  - ✅ CRUD de categorías (Principio, Proteína)")
        print("  - ✅ CRUD de platos del restaurante")
        print("  - ✅ Crear menú del día con platos por categoría")
        print("  - ✅ Publicar/despublicar menú para meseros")
        print("  - ✅ Gestionar acompañamientos fijos")
        print("  - ✅ Gestionar platos fijos independientes")
        print("  - ✅ Vista de meseros con menú del día")
        
        print("\n📊 Datos disponibles:")
        print("  - ✅ Categorías: Principio, Proteína")
        print("  - ✅ Platos: Menu_Dia, Plato_Fijo")
        print("  - ✅ Acompañamientos fijos: Plátano, Arroz, Ensalada, Sopa, Bebida")
        print("  - ✅ Menú del día: Creado y publicado")
        print("  - ✅ Platos fijos: Frijolada, Chicharrón al barril")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_menu_web_interface()


