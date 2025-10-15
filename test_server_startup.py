#!/usr/bin/env python3
"""
Script para probar que el servidor inicie correctamente
"""
import subprocess
import time
import requests
import sys

def test_server_startup():
    """Probar que el servidor inicie sin errores"""
    print("🚀 Probando inicio del servidor...")
    
    try:
        # Intentar hacer una petición simple al servidor
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"⚠️ Servidor respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor no está ejecutándose")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_restaurant_menu_endpoints():
    """Probar endpoints del sistema de menús del restaurante"""
    print("\n🍽️ Probando endpoints del sistema de menús...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Probar endpoint de categorías
        print("📋 Probando GET /api/v1/restaurant-menu/categorias/")
        response = requests.get(f"{base_url}/api/v1/restaurant-menu/categorias/", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categorías obtenidas: {data.get('total', 0)} categorías")
            return True
        else:
            print(f"❌ Error en categorías: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando endpoints: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando estado del servidor...")
    
    if test_server_startup():
        print("\n🎉 Servidor funcionando correctamente!")
        
        if test_restaurant_menu_endpoints():
            print("✅ Sistema de menús del restaurante funcionando!")
        else:
            print("⚠️ Problemas con el sistema de menús")
    else:
        print("❌ Servidor no está funcionando")
        print("Inicia el servidor con: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


