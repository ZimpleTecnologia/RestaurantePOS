#!/usr/bin/env python3
"""
Script para probar el módulo de gestión de menús
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.carta_restaurante import CartaRestaurante, MenuDia, MenuOpcion, TipoPlato
from decimal import Decimal
from datetime import date, timedelta

def test_menu_module():
    """Probar el módulo de gestión de menús"""
    print("🍽️ Probando módulo de gestión de menús...")
    
    try:
        db = next(get_db())
        
        # 1. Verificar platos disponibles
        print("\n📋 Verificando platos disponibles...")
        platos = db.query(CartaRestaurante).all()
        print(f"  - Total platos: {len(platos)}")
        
        platos_fijos = [p for p in platos if p.tipo == TipoPlato.FIJO]
        platos_variables = [p for p in platos if p.tipo == TipoPlato.VARIABLE]
        
        print(f"  - Platos fijos: {len(platos_fijos)}")
        print(f"  - Platos variables: {len(platos_variables)}")
        
        # 2. Verificar menús existentes
        print("\n📅 Verificando menús existentes...")
        menus = db.query(MenuDia).all()
        print(f"  - Total menús: {len(menus)}")
        
        for menu in menus:
            print(f"  - {menu.fecha}: {menu.nombre} (${menu.precio}) - {'Activo' if menu.activo else 'Inactivo'}")
        
        # 3. Verificar menú de hoy
        print("\n🗓️ Verificando menú de hoy...")
        today = date.today().strftime('%Y-%m-%d')
        menu_hoy = db.query(MenuDia).filter(MenuDia.fecha == today).first()
        
        if menu_hoy:
            print(f"  ✅ Menú de hoy encontrado: {menu_hoy.nombre}")
            print(f"  - Precio: ${menu_hoy.precio}")
            print(f"  - Estado: {'Activo' if menu_hoy.activo else 'Inactivo'}")
            
            # Verificar opciones del menú
            opciones = db.query(MenuOpcion).filter(MenuOpcion.menu_id == menu_hoy.menu_id).all()
            print(f"  - Opciones del menú: {len(opciones)}")
            
            for opcion in opciones:
                plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == opcion.producto_id).first()
                if plato:
                    tipo = "Fijo" if opcion.es_fijo else "Variable"
                    print(f"    - {plato.nombre} ({tipo})")
        else:
            print("  ❌ No hay menú para hoy")
        
        # 4. Crear menú de prueba si no existe
        if not menu_hoy:
            print("\n🔄 Creando menú de prueba...")
            
            # Buscar platos fijos y variables
            if len(platos_fijos) == 0 or len(platos_variables) == 0:
                print("  ⚠️ No hay suficientes platos para crear un menú")
                print("  Ejecuta primero: python create_simple_menu.py")
                return
            
            # Crear menú de prueba
            menu_prueba = MenuDia(
                fecha=today,
                nombre="Menú de Prueba - " + today,
                precio=Decimal('25.00'),
                descripcion="Menú de prueba para testing",
                activo=True
            )
            db.add(menu_prueba)
            db.flush()
            
            # Agregar platos fijos
            for plato in platos_fijos[:3]:  # Máximo 3 platos fijos
                opcion = MenuOpcion(
                    menu_id=menu_prueba.menu_id,
                    producto_id=plato.producto_id,
                    es_fijo=True
                )
                db.add(opcion)
                print(f"    ✅ Agregado plato fijo: {plato.nombre}")
            
            # Agregar platos variables
            for plato in platos_variables[:5]:  # Máximo 5 platos variables
                opcion = MenuOpcion(
                    menu_id=menu_prueba.menu_id,
                    producto_id=plato.producto_id,
                    es_fijo=False
                )
                db.add(opcion)
                print(f"    ✅ Agregado plato variable: {plato.nombre}")
            
            db.commit()
            print(f"  ✅ Menú de prueba creado: {menu_prueba.nombre}")
        
        print("\n🎉 Módulo de menús funcionando correctamente!")
        print(f"\n🌐 Puedes probarlo en:")
        print(f"  - Interfaz web: http://127.0.0.1:8000/menu-management")
        print(f"  - API: http://127.0.0.1:8000/api/v1/carta/menus/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_menu_module()
