#!/usr/bin/env python3
"""
Script para crear el menú PLATÓNICO de ejemplo
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.carta_restaurante import CartaRestaurante, MenuDia, MenuOpcion, TipoPlato, CategoriaPlato
from decimal import Decimal

def create_menu_platonic():
    """Crear el menú PLATÓNICO de ejemplo"""
    print("🔄 Creando menú PLATÓNICO de ejemplo...")
    
    try:
        db = next(get_db())
        
        # 1. Crear componentes fijos (si no existen)
        print("\n🔄 Creando componentes fijos...")
        componentes_fijos = [
            {"nombre": "Maduro", "descripcion": "Maduro frito", "precio_base": 0.00, "tipo": TipoPlato.FIJO, "categoria": CategoriaPlato.ACOMPANAMIENTO.value},
            {"nombre": "Arroz", "descripcion": "Arroz blanco", "precio_base": 0.00, "tipo": TipoPlato.FIJO, "categoria": CategoriaPlato.ACOMPANAMIENTO.value},
            {"nombre": "Ensalada", "descripcion": "Ensalada mixta", "precio_base": 0.00, "tipo": TipoPlato.FIJO, "categoria": CategoriaPlato.ACOMPANAMIENTO.value},
            {"nombre": "Sopa", "descripcion": "Sopa del día", "precio_base": 0.00, "tipo": TipoPlato.FIJO, "categoria": CategoriaPlato.ENTRADA.value},
            {"nombre": "Bebida", "descripcion": "Bebida del día", "precio_base": 0.00, "tipo": TipoPlato.FIJO, "categoria": CategoriaPlato.BEBIDA.value}
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
        
        # 2. Crear opciones seleccionables (si no existen)
        print("\n🔄 Creando opciones seleccionables...")
        opciones_seleccionables = [
            # SOPAS (ENTRADAS)
            {"nombre": "Crema de espinacas", "descripcion": "Crema de espinacas casera", "precio_base": 8.00, "tipo": TipoPlato.VARIABLE, "categoria": CategoriaPlato.ENTRADA.value},
            {"nombre": "Lentejas ahumadas", "descripcion": "Lentejas con sabor ahumado", "precio_base": 7.00, "tipo": TipoPlato.VARIABLE, "categoria": CategoriaPlato.ENTRADA.value},
            
            # PRINCIPIOS (ACOMPAÑAMIENTOS)
            {"nombre": "Vegetales salteados", "descripcion": "Vegetales frescos salteados", "precio_base": 6.00, "tipo": TipoPlato.VARIABLE, "categoria": CategoriaPlato.ACOMPANAMIENTO.value},
            
            # PROTEINAS (PLATOS PRINCIPALES)
            {"nombre": "Pollo sudado", "descripcion": "Pollo sudado con especias", "precio_base": 12.00, "tipo": TipoPlato.VARIABLE, "categoria": CategoriaPlato.PLATO_PRINCIPAL.value},
            {"nombre": "Carne de cerdo en salsa de lulo", "descripcion": "Carne de cerdo con salsa de lulo", "precio_base": 15.00, "tipo": TipoPlato.VARIABLE, "categoria": CategoriaPlato.PLATO_PRINCIPAL.value},
            {"nombre": "Chuleta de cerdo", "descripcion": "Chuleta de cerdo a la plancha", "precio_base": 14.00, "tipo": TipoPlato.VARIABLE, "categoria": CategoriaPlato.PLATO_PRINCIPAL.value},
            {"nombre": "Hígado encebollado", "descripcion": "Hígado encebollado tradicional", "precio_base": 13.00, "tipo": TipoPlato.VARIABLE, "categoria": CategoriaPlato.PLATO_PRINCIPAL.value}
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
        
        # 3. Crear el menú del día PLATÓNICO
        print("\n🔄 Creando menú del día PLATÓNICO...")
        
        # Verificar si ya existe un menú para hoy
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        
        existing_menu = db.query(MenuDia).filter(MenuDia.fecha == today).first()
        if existing_menu:
            print(f"ℹ️ Ya existe un menú para {today}, eliminando...")
            db.delete(existing_menu)
            db.flush()
        
        # Crear nuevo menú
        menu_platonic = MenuDia(
            fecha=today,
            nombre="PLATÓNICO - Amor al primer bocado",
            precio=Decimal('25.00'),
            descripcion="Menú del día con opciones seleccionables por categoría",
            activo=True
        )
        db.add(menu_platonic)
        db.flush()  # Para obtener el ID del menú
        
        print(f"✅ Creado menú: {menu_platonic.nombre}")
        
        # 4. Crear las opciones del menú
        print("\n🔄 Creando opciones del menú...")
        
        # Componentes fijos (se incluyen automáticamente)
        for plato_id in platos_fijos_ids:
            opcion = MenuOpcion(
                menu_id=menu_platonic.menu_id,
                producto_id=plato_id,
                es_fijo=True
            )
            db.add(opcion)
            print(f"✅ Agregado componente fijo: ID {plato_id}")
        
        # Opciones seleccionables
        for plato_id in platos_variables_ids:
            opcion = MenuOpcion(
                menu_id=menu_platonic.menu_id,
                producto_id=plato_id,
                es_fijo=False
            )
            db.add(opcion)
            print(f"✅ Agregada opción seleccionable: ID {plato_id}")
        
        # Confirmar cambios
        db.commit()
        
        print("\n🎉 ¡Menú PLATÓNICO creado exitosamente!")
        print(f"\n📋 Resumen:")
        print(f"  - Menú: {menu_platonic.nombre}")
        print(f"  - Fecha: {menu_platonic.fecha}")
        print(f"  - Precio: ${menu_platonic.precio}")
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
    create_menu_platonic()
