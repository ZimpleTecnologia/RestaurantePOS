#!/usr/bin/env python3
"""
Script para probar el usuario de inventario
"""
import sys
import os
import requests

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

def test_inventory_user():
    """Probar login del usuario de inventario"""
    base_url = "http://localhost:8000"
    
    print("🧪 Probando usuario de inventario...")
    
    # Datos de login
    login_data = {
        "username": "adminana",
        "password": "54321"
    }
    
    try:
        # Intentar login
        response = requests.post(f"{base_url}/api/v1/auth/login", data=login_data)
        
        if response.status_code == 200:
            print("✅ Login exitoso")
            token_data = response.json()
            token = token_data.get("access_token")
            
            if token:
                print(f"🔑 Token obtenido: {token[:20]}...")
                
                # Probar acceso a inventario (debería funcionar)
                headers = {"Authorization": f"Bearer {token}"}
                inventory_response = requests.get(f"{base_url}/inventory", headers=headers)
                print(f"📦 Acceso a inventario: {inventory_response.status_code}")
                
                # Probar acceso a productos (debería redirigir)
                products_response = requests.get(f"{base_url}/products", headers=headers, allow_redirects=False)
                print(f"🛒 Acceso a productos: {products_response.status_code}")
                if products_response.status_code == 302:
                    print("✅ Redirección correcta a módulo en desarrollo")
                
                # Probar acceso a caja (debería redirigir)
                caja_response = requests.get(f"{base_url}/caja-ventas", headers=headers, allow_redirects=False)
                print(f"💰 Acceso a caja: {caja_response.status_code}")
                if caja_response.status_code == 302:
                    print("✅ Redirección correcta a módulo en desarrollo")
                
                return True
            else:
                print("❌ No se obtuvo token")
                return False
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Probando usuario de inventario...")
    
    success = test_inventory_user()
    
    if success:
        print("✅ Pruebas completadas exitosamente")
    else:
        print("❌ Error en las pruebas")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
