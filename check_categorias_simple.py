#!/usr/bin/env python3
"""
Script simple para verificar categorías
"""

import requests
import json

def verificar_categorias():
    """Verificar categorías desde la API"""
    try:
        # Verificar categorías disponibles
        print("🔍 Verificando categorías disponibles...")
        response = requests.get("http://localhost:8000/api/v1/menu-restructured/categorias/")
        if response.status_code == 200:
            data = response.json()
            print("📋 Categorías disponibles:")
            for cat in data.get('categorias', []):
                print(f"   ID: {cat['id']}, Nombre: '{cat['nombre']}', Activo: {cat['activo']}")
        else:
            print(f"❌ Error obteniendo categorías: {response.status_code}")
        
        # Verificar opciones y sus categorías
        print("\n🍽️ Verificando opciones...")
        response = requests.get("http://localhost:8000/api/v1/menu-restructured/opciones/")
        if response.status_code == 200:
            data = response.json()
            print("📋 Opciones y sus categorías:")
            for opcion in data.get('opciones', []):
                categoria_nombre = opcion.get('categoria', {}).get('nombre', 'Sin categoría') if opcion.get('categoria') else 'Sin categoría'
                print(f"   '{opcion['nombre']}' -> Categoría: '{categoria_nombre}'")
        else:
            print(f"❌ Error obteniendo opciones: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_categorias()
