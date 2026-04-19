#!/usr/bin/env python3
"""
Script para probar el endpoint from-carta directamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_endpoint_direct():
    """Probar el endpoint from-carta directamente"""
    try:
        print("🔧 Probando endpoint from-carta directamente...")
        
        # URL del endpoint
        url = "http://localhost:8000/api/v1/menu-restructured/menus/from-carta/"
        
        # Parámetros de prueba
        params = {
            'fecha': '2025-09-24',
            'nombre': 'Test Menu Direct',
            'descripcion': 'Test desde script',
            'precio': 14000,
            'platos_fijos_ids': '1,2,3',
            'platos_variables_ids': '4,5,6'
        }
        
        print(f"📡 Enviando request a: {url}")
        print(f"📋 Parámetros: {params}")
        
        # Hacer la petición
        response = requests.post(url, params=params)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"📋 Response JSON: {json.dumps(data, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Endpoint funcionando correctamente!")
            return True
        else:
            print("❌ Endpoint con problemas!")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False

def test_endpoint_simple():
    """Probar el endpoint simple primero"""
    try:
        print("\n🔧 Probando endpoint simple...")
        
        # URL del endpoint simple
        url = "http://localhost:8000/api/v1/menu-restructured/menus/"
        
        # Parámetros de prueba
        params = {
            'fecha': '2025-09-25',
            'nombre': 'Test Menu Simple',
            'descripcion': 'Test simple',
            'precio': 14000,
            'opciones_ids': '1,2,3'
        }
        
        print(f"📡 Enviando request a: {url}")
        print(f"📋 Parámetros: {params}")
        
        # Hacer la petición
        response = requests.post(url, params=params)
        
        print(f"📊 Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"📋 Response JSON: {json.dumps(data, indent=2)}")
        except:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Endpoint simple funcionando!")
            return True
        else:
            print("❌ Endpoint simple con problemas!")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba simple: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Script de Prueba de Endpoints")
    print("=" * 50)
    
    # Probar endpoint simple primero
    simple_success = test_endpoint_simple()
    
    # Probar endpoint from-carta
    from_carta_success = test_endpoint_direct()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"   Endpoint simple: {'✅ OK' if simple_success else '❌ ERROR'}")
    print(f"   Endpoint from-carta: {'✅ OK' if from_carta_success else '❌ ERROR'}")
    
    if simple_success and from_carta_success:
        print("\n🎉 Todos los endpoints funcionando correctamente!")
    else:
        print("\n⚠️ Algunos endpoints tienen problemas.")
        print("   Revisa los logs del servidor para más detalles.")





