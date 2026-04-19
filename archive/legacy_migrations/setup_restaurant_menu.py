#!/usr/bin/env python3
"""
Script simple para configurar el sistema de menús del restaurante
"""
import requests
import json
from datetime import date

def setup_restaurant_menu():
    """Configurar el sistema de menús del restaurante"""
    print("🍽️ Configurando Sistema de Menús del Restaurante...")
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
        
        # 2. Crear categorías por defecto
        print("\n📋 Creando categorías por defecto...")
        categorias_default = [
            {"nombre": "Principio", "descripcion": "Platos de entrada o principio", "orden": 1},
            {"nombre": "Proteína", "descripcion": "Platos principales con proteína", "orden": 2}
        ]
        
        for categoria in categorias_default:
            try:
                response = requests.post(
                    f"{base_url}/api/v1/restaurant-menu/categorias/",
                    json=categoria,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    print(f"✅ Categoría '{categoria['nombre']}' creada")
                elif response.status_code == 400 and "Ya existe" in response.text:
                    print(f"⚠️ Categoría '{categoria['nombre']}' ya existe")
                else:
                    print(f"❌ Error creando categoría '{categoria['nombre']}': {response.text}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # 3. Crear acompañamientos fijos
        print("\n🥗 Creando acompañamientos fijos...")
        acompanamientos_default = [
            {"nombre": "Plátano maduro", "descripcion": "Plátano maduro frito", "orden": 1},
            {"nombre": "Arroz", "descripcion": "Arroz blanco", "orden": 2},
            {"nombre": "Ensalada", "descripcion": "Ensalada fresca", "orden": 3},
            {"nombre": "Sopa", "descripcion": "Sopa del día", "orden": 4},
            {"nombre": "Bebida", "descripcion": "Bebida del día", "orden": 5}
        ]
        
        for acompanamiento in acompanamientos_default:
            try:
                response = requests.post(
                    f"{base_url}/api/v1/restaurant-menu/acompanamientos/",
                    json=acompanamiento,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    print(f"✅ Acompañamiento '{acompanamiento['nombre']}' creado")
                elif response.status_code == 400 and "Ya existe" in response.text:
                    print(f"⚠️ Acompañamiento '{acompanamiento['nombre']}' ya existe")
                else:
                    print(f"❌ Error creando acompañamiento '{acompanamiento['nombre']}': {response.text}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # 4. Crear platos de ejemplo
        print("\n🍽️ Creando platos de ejemplo...")
        platos_ejemplo = [
            # Platos para menú del día
            {"nombre": "Verduras a la crema", "descripcion": "Verduras frescas en crema", "precio": 0.0, "tipo": "Menu_Dia"},
            {"nombre": "Frijoles", "descripcion": "Frijoles tradicionales", "precio": 0.0, "tipo": "Menu_Dia"},
            {"nombre": "Pechuga a la plancha", "descripcion": "Pechuga de pollo a la plancha", "precio": 0.0, "tipo": "Menu_Dia"},
            {"nombre": "Carne de cerdo", "descripcion": "Carne de cerdo asada", "precio": 0.0, "tipo": "Menu_Dia"},
            {"nombre": "Hígado encebollado", "descripcion": "Hígado con cebolla", "precio": 0.0, "tipo": "Menu_Dia"},
            
            # Platos fijos
            {"nombre": "Frijolada", "descripcion": "Frijolada tradicional", "precio": 15000.0, "tipo": "Plato_Fijo"},
            {"nombre": "Chicharrón al barril", "descripcion": "Chicharrón al barril", "precio": 18000.0, "tipo": "Plato_Fijo"}
        ]
        
        for plato in platos_ejemplo:
            try:
                response = requests.post(
                    f"{base_url}/api/v1/restaurant-menu/platos/",
                    json=plato,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    print(f"✅ Plato '{plato['nombre']}' creado")
                elif response.status_code == 400 and "Ya existe" in response.text:
                    print(f"⚠️ Plato '{plato['nombre']}' ya existe")
                else:
                    print(f"❌ Error creando plato '{plato['nombre']}': {response.text}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # 5. Crear menú de ejemplo para hoy
        print("\n📅 Creando menú de ejemplo para hoy...")
        try:
            menu_data = {
                "fecha": str(date.today()),
                "nombre": f"Almuerzo del {date.today().strftime('%d/%m/%Y')}",
                "descripcion": "Menú especial del día",
                "categorias_platos": {
                    "Principio": [1, 2],  # Verduras a la crema, Frijoles
                    "Proteína": [3, 4, 5]  # Pechuga, Carne, Hígado
                }
            }
            
            response = requests.post(
                f"{base_url}/api/v1/restaurant-menu/menus/",
                json=menu_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Menú creado: {data.get('nombre', 'N/A')} (ID: {data.get('id', 'N/A')})")
                
                # Publicar el menú
                menu_id = data.get('id')
                if menu_id:
                    try:
                        response = requests.put(f"{base_url}/api/v1/restaurant-menu/menus/{menu_id}/publicar")
                        if response.status_code == 200:
                            print("✅ Menú publicado para meseros")
                        else:
                            print(f"⚠️ Error publicando menú: {response.text}")
                    except Exception as e:
                        print(f"⚠️ Error publicando menú: {e}")
            else:
                print(f"❌ Error creando menú: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Configuración del sistema de menús completada!")
        print("\n📋 Datos creados:")
        print("  - ✅ Categorías: Principio, Proteína")
        print("  - ✅ Acompañamientos fijos: Plátano, Arroz, Ensalada, Sopa, Bebida")
        print("  - ✅ Platos de ejemplo: Verduras, Frijoles, Pechuga, Carne, Hígado")
        print("  - ✅ Platos fijos: Frijolada, Chicharrón al barril")
        print("  - ✅ Menú del día: Creado y publicado")
        
        print("\n🌐 URLs disponibles:")
        print("  - Home: http://127.0.0.1:8000/")
        print("  - Documentación API: http://127.0.0.1:8000/docs")
        print("  - Gestión de Menús: http://127.0.0.1:8000/admin/menus")
        print("  - Vista de Meseros: http://127.0.0.1:8000/meseros/menus")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    setup_restaurant_menu()


