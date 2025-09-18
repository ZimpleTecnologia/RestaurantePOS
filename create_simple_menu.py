#!/usr/bin/env python3
"""
Script para crear un menú simple y funcional
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.carta_restaurante import CartaRestaurante, MenuDia, MenuOpcion, TipoPlato
from decimal import Decimal

def create_simple_menu():
    """Crear un menú simple y funcional"""
    print("🔄 Creando menú simple...")
    
    try:
        db = next(get_db())
        
        # 1. Crear componentes fijos (sin categorías problemáticas)
        print("\n🔄 Creando componentes fijos...")
        componentes_fijos = [
            {"nombre": "Arroz", "descripcion": "Arroz blanco", "precio_base": 0.00, "tipo": TipoPlato.FIJO, "categoria": "Otro"},
            {"nombre": "Ensalada", "descripcion": "Ensalada mixta", "precio_base": 0.00, "tipo": TipoPlato.FIJO, "categoria": "Otro"},
            {"nombre": "Bebida", "descripcion": "Bebida del día", "precio_base": 0.00, "tipo": TipoPlato.FIJO, "categoria": "Bebida"}
        ]
        
        platos_fijos_ids = []
        for componente in componentes_fijos:
            # Verificar si ya existe
            existing = db.query(CartaRestaurante).filter(
                CartaRestaurante.nombre == componente["nombre"],
                CartaRestaurante.tipo == componente["tipo"]
            ).first()
            
            if not existing:
                plato = CartaRestaurante(**componente)
                db.add(plato)
                db.flush()  # Para obtener el ID
                platos_fijos_ids.append(plato.producto_id)
                print(f"✅ Creado: {componente['nombre']}")
            else:
                platos_fijos_ids.append(existing.producto_id)
                print(f"ℹ️ Ya existe: {componente['nombre']}")
        
        # 2. Crear opciones seleccionables
        print("\n🔄 Creando opciones seleccionables...")
        opciones_seleccionables = [
            # SOPAS
            {"nombre": "Sopa de pollo", "descripcion": "Sopa de pollo casera", "precio_base": 8.00, "tipo": TipoPlato.VARIABLE, "categoria": "Entrada"},
            {"nombre": "Crema de verduras", "descripcion": "Crema de verduras frescas", "precio_base": 7.00, "tipo": TipoPlato.VARIABLE, "categoria": "Entrada"},
            
            # PLATOS PRINCIPALES
            {"nombre": "Pollo a la plancha", "descripcion": "Pollo a la plancha con especias", "precio_base": 12.00, "tipo": TipoPlato.VARIABLE, "categoria": "Plato Principal"},
            {"nombre": "Carne de res", "descripcion": "Carne de res a la parrilla", "precio_base": 15.00, "tipo": TipoPlato.VARIABLE, "categoria": "Plato Principal"},
            {"nombre": "Pescado frito", "descripcion": "Pescado fresco frito", "precio_base": 14.00, "tipo": TipoPlato.VARIABLE, "categoria": "Plato Principal"}
        ]
        
        platos_variables_ids = []
        for opcion in opciones_seleccionables:
            # Verificar si ya existe
            existing = db.query(CartaRestaurante).filter(
                CartaRestaurante.nombre == opcion["nombre"],
                CartaRestaurante.tipo == opcion["tipo"]
            ).first()
            
            if not existing:
                plato = CartaRestaurante(**opcion)
                db.add(plato)
                db.flush()  # Para obtener el ID
                platos_variables_ids.append(plato.producto_id)
                print(f"✅ Creado: {opcion['nombre']}")
            else:
                platos_variables_ids.append(existing.producto_id)
                print(f"ℹ️ Ya existe: {opcion['nombre']}")
        
        # 3. Crear el menú del día
        print("\n🔄 Creando menú del día...")
        
        # Verificar si ya existe un menú para hoy
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        
        existing_menu = db.query(MenuDia).filter(MenuDia.fecha == today).first()
        if existing_menu:
            print(f"ℹ️ Ya existe un menú para {today}, eliminando...")
            db.delete(existing_menu)
            db.flush()
        
        # Crear nuevo menú
        menu_simple = MenuDia(
            fecha=today,
            nombre="Menú del Día - Especial",
            precio=Decimal('20.00'),
            descripcion="Menú del día con opciones seleccionables",
            activo=True
        )
        db.add(menu_simple)
        db.flush()  # Para obtener el ID del menú
        
        print(f"✅ Creado menú: {menu_simple.nombre}")
        
        # 4. Crear las opciones del menú
        print("\n🔄 Creando opciones del menú...")
        
        # Componentes fijos (se incluyen automáticamente)
        for plato_id in platos_fijos_ids:
            opcion = MenuOpcion(
                menu_id=menu_simple.menu_id,
                producto_id=plato_id,
                es_fijo=True
            )
            db.add(opcion)
            print(f"✅ Agregado componente fijo: ID {plato_id}")
        
        # Opciones seleccionables
        for plato_id in platos_variables_ids:
            opcion = MenuOpcion(
                menu_id=menu_simple.menu_id,
                producto_id=plato_id,
                es_fijo=False
            )
            db.add(opcion)
            print(f"✅ Agregada opción seleccionable: ID {plato_id}")
        
        # Confirmar cambios
        db.commit()
        
        print("\n🎉 ¡Menú simple creado exitosamente!")
        print(f"\n📋 Resumen:")
        print(f"  - Menú: {menu_simple.nombre}")
        print(f"  - Fecha: {menu_simple.fecha}")
        print(f"  - Precio: ${menu_simple.precio}")
        print(f"  - Componentes fijos: {len(platos_fijos_ids)}")
        print(f"  - Opciones seleccionables: {len(platos_variables_ids)}")
        
        print(f"\n🌐 Puedes probarlo en:")
        print(f"  - Interfaz web: http://127.0.0.1:8000/carta-restaurante/admin")
        print(f"  - API: http://127.0.0.1:8000/api/v1/carta/menus/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_simple_menu()
