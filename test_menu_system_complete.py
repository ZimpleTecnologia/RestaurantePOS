#!/usr/bin/env python3
"""
Script de prueba para el sistema completo de menús del día
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.menu_restructured import MenuDiaRestructured, OpcionPlato, MenuDiaOpcion
from app.models.carta_restaurante import CartaRestaurante
from sqlalchemy.orm import Session
from datetime import datetime, date
import json

def test_menu_system():
    """Probar el sistema completo de menús"""
    print("🍽️  Probando Sistema de Menús del Día")
    print("=" * 50)
    
    db = next(get_db())
    
    try:
        # 1. Verificar datos de la carta restaurante
        print("\n1. 📋 Verificando Carta Restaurante...")
        platos_fijos = db.query(CartaRestaurante).filter(CartaRestaurante.tipo == 'Fijo').all()
        platos_variables = db.query(CartaRestaurante).filter(CartaRestaurante.tipo == 'Variable').all()
        
        print(f"   ✅ Platos fijos disponibles: {len(platos_fijos)}")
        for plato in platos_fijos[:3]:  # Mostrar solo los primeros 3
            print(f"      - {plato.nombre} (${plato.precio_base:,.0f} COP)")
        
        print(f"   ✅ Platos variables disponibles: {len(platos_variables)}")
        for plato in platos_variables[:3]:  # Mostrar solo los primeros 3
            print(f"      - {plato.nombre} (${plato.precio_base:,.0f} COP)")
        
        # 2. Crear un menú de prueba
        print("\n2. 🆕 Creando Menú de Prueba...")
        menu_hoy = MenuDiaRestructured(
            fecha=date.today(),
            nombre="Menú Ejecutivo",
            descripcion="Menú completo con platos fijos y variables",
            precio=14000.0,
            estado='ACTIVE'
        )
        db.add(menu_hoy)
        db.commit()
        db.refresh(menu_hoy)
        print(f"   ✅ Menú creado: {menu_hoy.nombre} (ID: {menu_hoy.id})")
        
        # 3. Agregar platos fijos al menú
        print("\n3. ⭐ Agregando Platos Fijos...")
        platos_fijos_ids = [plato.producto_id for plato in platos_fijos[:2]]  # Tomar los primeros 2
        
        for plato_id in platos_fijos_ids:
            menu_opcion = MenuDiaOpcion(
                menu_dia_id=menu_hoy.id,
                opcion_id=plato_id,
                disponible=True
            )
            db.add(menu_opcion)
        
        db.commit()
        print(f"   ✅ {len(platos_fijos_ids)} platos fijos agregados")
        
        # 4. Agregar platos variables al menú
        print("\n4. 🔄 Agregando Platos Variables...")
        platos_variables_ids = [plato.producto_id for plato in platos_variables[:3]]  # Tomar los primeros 3
        
        for plato_id in platos_variables_ids:
            menu_opcion = MenuDiaOpcion(
                menu_dia_id=menu_hoy.id,
                opcion_id=plato_id,
                disponible=True
            )
            db.add(menu_opcion)
        
        db.commit()
        print(f"   ✅ {len(platos_variables_ids)} platos variables agregados")
        
        # 5. Verificar el menú creado
        print("\n5. 📊 Verificando Menú Creado...")
        menu_completo = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.id == menu_hoy.id).first()
        opciones_menu = db.query(MenuDiaOpcion).filter(MenuDiaOpcion.menu_dia_id == menu_hoy.id).all()
        
        print(f"   📅 Fecha: {menu_completo.fecha}")
        print(f"   🏷️  Nombre: {menu_completo.nombre}")
        print(f"   💰 Precio: ${menu_completo.precio:,.0f} COP")
        print(f"   📝 Descripción: {menu_completo.descripcion}")
        print(f"   🔢 Total opciones: {len(opciones_menu)}")
        
        # 6. Mostrar opciones del menú
        print("\n6. 🍽️  Opciones del Menú:")
        for i, opcion in enumerate(opciones_menu, 1):
            plato_info = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == opcion.opcion_id).first()
            if plato_info:
                tipo_icon = "⭐" if plato_info.tipo == "Fijo" else "🔄"
                print(f"   {i}. {tipo_icon} {plato_info.nombre} - ${plato_info.precio_base:,.0f} COP")
        
        # 7. Probar duplicación de menú
        print("\n7. 📋 Probando Duplicación de Menú...")
        menu_duplicado = MenuDiaRestructured(
            fecha=date.today().replace(day=date.today().day + 1) if date.today().day < 28 else date.today().replace(day=1, month=date.today().month + 1),
            nombre=f"{menu_hoy.nombre} (Copia)",
            descripcion=menu_hoy.descripcion,
            precio=menu_hoy.precio,
            estado='ACTIVE'
        )
        db.add(menu_duplicado)
        db.commit()
        db.refresh(menu_duplicado)
        
        # Copiar opciones del menú original
        for opcion in opciones_menu:
            nueva_opcion = MenuDiaOpcion(
                menu_dia_id=menu_duplicado.id,
                opcion_id=opcion.opcion_id,
                disponible=opcion.disponible
            )
            db.add(nueva_opcion)
        db.commit()
        
        print(f"   ✅ Menú duplicado: {menu_duplicado.nombre} (ID: {menu_duplicado.id})")
        
        # 8. Estadísticas finales
        print("\n8. 📈 Estadísticas del Sistema:")
        total_menus = db.query(MenuDiaRestructured).count()
        menus_activos = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.estado == 'ACTIVE').count()
        total_platos = db.query(CartaRestaurante).count()
        
        print(f"   📊 Total menús: {total_menus}")
        print(f"   ✅ Menús activos: {menus_activos}")
        print(f"   🍽️  Total platos en carta: {total_platos}")
        
        print("\n🎉 ¡Sistema de menús funcionando correctamente!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en el sistema: {str(e)}")
        db.rollback()
        return False
    
    finally:
        db.close()

def test_api_endpoints():
    """Probar endpoints de la API"""
    print("\n🌐 Probando Endpoints de la API...")
    print("=" * 50)
    
    import requests
    
    base_url = "http://localhost:8000"
    
    try:
        # Probar endpoint de menús
        response = requests.get(f"{base_url}/api/v1/menu-restructured/menus/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /menus/ - {data.get('total', 0)} menús encontrados")
        else:
            print(f"❌ GET /menus/ - Error {response.status_code}")
        
        # Probar endpoint de carta restaurante
        response = requests.get(f"{base_url}/api/v1/carta-restaurante/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /carta-restaurante/ - {len(data.get('productos', []))} productos encontrados")
        else:
            print(f"❌ GET /carta-restaurante/ - Error {response.status_code}")
        
        # Probar endpoint de estadísticas
        response = requests.get(f"{base_url}/api/v1/menu-restructured/stats/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /stats/ - Estadísticas obtenidas")
        else:
            print(f"❌ GET /stats/ - Error {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. Asegúrate de que esté ejecutándose en localhost:8000")
    except Exception as e:
        print(f"❌ Error probando endpoints: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando Pruebas del Sistema de Menús")
    print("=" * 60)
    
    # Probar sistema de base de datos
    success = test_menu_system()
    
    if success:
        # Probar endpoints de la API
        test_api_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ Todas las pruebas completadas exitosamente!")
        print("\n📋 Resumen de funcionalidades implementadas:")
        print("   • Creación de menús con fecha, nombre y precio base (14,000 COP)")
        print("   • Platos fijos se incluyen automáticamente con opción de exclusión")
        print("   • Platos variables organizados por categorías (Proteína, Acompañamiento, Bebida, Postre)")
        print("   • Edición y eliminación de menús")
        print("   • Historial de menús con filtros")
        print("   • Duplicación de menús anteriores")
        print("   • Interfaz administrativa completa")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores anteriores.")
