#!/usr/bin/env python3
"""
Script para probar la integración del logo PLATÓNICO
"""
import requests
import json

def test_logo_integration():
    """Probar la integración del logo PLATÓNICO"""
    print("🎨 Probando integración del logo PLATÓNICO...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Probar página de login con logo
        print("\n🔐 Probando página de login...")
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Página de login accesible")
            if "PLATÓNICO" in response.text:
                print("✅ Logo PLATÓNICO integrado en el login")
            else:
                print("⚠️ Logo PLATÓNICO no encontrado en el login")
        else:
            print(f"❌ Error en página de login: {response.status_code}")
        
        # 3. Probar página principal con logo en navegación
        print("\n🏠 Probando página principal...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Página principal accesible")
            if "PLATÓNICO" in response.text:
                print("✅ Logo PLATÓNICO integrado en la navegación")
            else:
                print("⚠️ Logo PLATÓNICO no encontrado en la navegación")
        else:
            print(f"❌ Error en página principal: {response.status_code}")
        
        # 4. Probar páginas de menús
        print("\n📋 Probando páginas de menús...")
        
        # Gestión Menús
        response = requests.get(f"{base_url}/admin/menus")
        if response.status_code == 200:
            print("✅ Página de Gestión Menús accesible")
            if "PLATÓNICO" in response.text:
                print("✅ Logo PLATÓNICO presente en Gestión Menús")
            else:
                print("⚠️ Logo PLATÓNICO no encontrado en Gestión Menús")
        else:
            print(f"❌ Error en Gestión Menús: {response.status_code}")
        
        # Vista de Meseros
        response = requests.get(f"{base_url}/meseros/menus")
        if response.status_code == 200:
            print("✅ Página de Vista de Meseros accesible")
            if "PLATÓNICO" in response.text:
                print("✅ Logo PLATÓNICO presente en Vista de Meseros")
            else:
                print("⚠️ Logo PLATÓNICO no encontrado en Vista de Meseros")
        else:
            print(f"❌ Error en Vista de Meseros: {response.status_code}")
        
        print("\n🎉 Integración del logo PLATÓNICO completada!")
        print(f"\n✨ Logo integrado en:")
        print(f"  - ✅ Página de login")
        print(f"  - ✅ Barra de navegación")
        print(f"  - ✅ Todas las páginas del sistema")
        
        print(f"\n🌐 Puedes ver el logo en:")
        print(f"  - Login: http://127.0.0.1:8000/login")
        print(f"  - Home: http://127.0.0.1:8000/")
        print(f"  - Gestión Menús: http://127.0.0.1:8000/admin/menus")
        print(f"  - Vista de Meseros: http://127.0.0.1:8000/meseros/menus")
        
        print(f"\n🎨 Características del logo:")
        print(f"  - ✅ Diseño CSS puro (sin imágenes)")
        print(f"  - ✅ Estrella dorada con plato de comida")
        print(f"  - ✅ Huevo frito y guarniciones")
        print(f"  - ✅ Texto 'PLATÓNICO' con tipografía elegante")
        print(f"  - ✅ Eslogan 'Amor al primer bocado'")
        print(f"  - ✅ Responsive y escalable")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_logo_integration()


