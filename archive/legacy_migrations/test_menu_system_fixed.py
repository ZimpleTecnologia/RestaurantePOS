#!/usr/bin/env python3
"""
Script de prueba para el sistema de menús reestructurado
Prueba la funcionalidad completa del sistema
"""

import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.menu_restructured import (
    MenuDiaRestructured, 
    OpcionPlato, 
    MenuDiaOpcion,
    CategoriaPlatoVariable
)
from app.models.carta_restaurante import CartaRestaurante

def test_menu_system():
    """Probar el sistema completo de menús"""
    print("🚀 Iniciando Pruebas del Sistema de Menús")
    print("=" * 60)
    print("🍽️  Probando Sistema de Menús del Día")
    print("=" * 50)
    
    try:
        # Obtener sesión de base de datos
        db = next(get_db())
        
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
        
        # 2. Verificar opciones existentes en opciones_platos
        print("\n2. 🔍 Verificando Opciones en Sistema...")
        opciones_existentes = db.query(OpcionPlato).all()
        print(f"   ✅ Opciones existentes: {len(opciones_existentes)}")
        
        if len(opciones_existentes) == 0:
            print("   ⚠️  No hay opciones en el sistema. Creando opciones desde Carta Restaurante...")
            
            # Crear categorías si no existen
            categorias_data = [
                {"nombre": "Proteína", "descripcion": "Platos principales con proteína"},
                {"nombre": "Acompañamiento", "descripcion": "Guarniciones y acompañamientos"},
                {"nombre": "Bebida", "descripcion": "Bebidas del menú"},
                {"nombre": "Postre", "descripcion": "Postres y dulces"}
            ]
            
            for cat_data in categorias_data:
                categoria = CategoriaPlatoVariable(**cat_data)
                db.add(categoria)
            db.commit()
            
            # Crear opciones desde carta restaurante
            for plato in platos_fijos + platos_variables:
                opcion = OpcionPlato(
                    nombre=plato.nombre,
                    descripcion=plato.descripcion,
                    tipo=plato.tipo,
                    precio=plato.precio_base,
                    activo=plato.activo
                )
                db.add(opcion)
            db.commit()
            
            print("   ✅ Opciones creadas desde Carta Restaurante")
        
        # 3. Crear un menú de prueba
        print("\n3. 🆕 Creando Menú de Prueba...")
        
        # Verificar si ya existe un menú para hoy
        menu_existente = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.fecha == date.today()).first()
        
        if menu_existente:
            print(f"   ⚠️  Ya existe un menú para hoy: {menu_existente.nombre} (ID: {menu_existente.id})")
            menu_hoy = menu_existente
        else:
            menu_hoy = MenuDiaRestructured(
                fecha=date.today(),
                nombre="Menú Ejecutivo",
                precio=Decimal('14000.00'),
                estado='ACTIVE',
                descripcion="Menú completo con platos fijos y variables"
            )
            db.add(menu_hoy)
            db.commit()
            db.refresh(menu_hoy)
            print(f"   ✅ Menú creado: {menu_hoy.nombre} (ID: {menu_hoy.id})")
        
        # 4. Verificar opciones existentes en el menú
        print("\n4. 🔍 Verificando Opciones del Menú...")
        opciones_existentes = db.query(MenuDiaOpcion).filter(MenuDiaOpcion.menu_dia_id == menu_hoy.id).all()
        
        if opciones_existentes:
            print(f"   ✅ El menú ya tiene {len(opciones_existentes)} opciones")
            for opcion in opciones_existentes:
                opcion_info = db.query(OpcionPlato).filter(OpcionPlato.id == opcion.opcion_id).first()
                if opcion_info:
                    tipo_icon = "⭐" if opcion_info.tipo == "Fijo" else "🔄"
                    print(f"      {tipo_icon} {opcion_info.nombre}")
        else:
            # Agregar platos fijos al menú
            print("\n5. ⭐ Agregando Platos Fijos...")
            opciones_fijas = db.query(OpcionPlato).filter(OpcionPlato.tipo == 'Fijo').limit(2).all()
            
            for opcion in opciones_fijas:
                menu_opcion = MenuDiaOpcion(
                    menu_dia_id=menu_hoy.id,
                    opcion_id=opcion.id,
                    disponible=True
                )
                db.add(menu_opcion)
                print(f"   ✅ Agregado: {opcion.nombre}")
            
            # Agregar platos variables al menú
            print("\n6. 🔄 Agregando Platos Variables...")
            opciones_variables = db.query(OpcionPlato).filter(OpcionPlato.tipo == 'Variable').limit(3).all()
            
            for opcion in opciones_variables:
                menu_opcion = MenuDiaOpcion(
                    menu_dia_id=menu_hoy.id,
                    opcion_id=opcion.id,
                    disponible=True
                )
                db.add(menu_opcion)
                print(f"   ✅ Agregado: {opcion.nombre}")
            
            db.commit()
        
        # 5. Verificar menú completo
        print("\n5. 📋 Verificando Menú Completo...")
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
            opcion_info = db.query(OpcionPlato).filter(OpcionPlato.id == opcion.opcion_id).first()
            if opcion_info:
                tipo_icon = "⭐" if opcion_info.tipo == "Fijo" else "🔄"
                print(f"   {i}. {tipo_icon} {opcion_info.nombre} - ${opcion_info.precio:,.0f} COP")
        
        # 7. Probar duplicación de menú
        print("\n7. 📋 Probando Duplicación de Menú...")
        
        # Buscar una fecha disponible para duplicar
        fecha_duplicado = date.today()
        for i in range(1, 30):  # Buscar en los próximos 30 días
            fecha_candidata = date.today() + timedelta(days=i)
            menu_existente = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.fecha == fecha_candidata).first()
            if not menu_existente:
                fecha_duplicado = fecha_candidata
                break
        
        menu_duplicado = MenuDiaRestructured(
            fecha=fecha_duplicado,
            nombre="Menú Ejecutivo (Duplicado)",
            precio=menu_completo.precio,
            estado='DRAFT',
            descripcion=f"Duplicado de {menu_completo.nombre}"
        )
        db.add(menu_duplicado)
        db.commit()
        db.refresh(menu_duplicado)
        
        # Duplicar opciones
        for opcion_original in opciones_menu:
            nueva_opcion = MenuDiaOpcion(
                menu_dia_id=menu_duplicado.id,
                opcion_id=opcion_original.opcion_id,
                disponible=opcion_original.disponible
            )
            db.add(nueva_opcion)
        db.commit()
        
        print(f"   ✅ Menú duplicado: {menu_duplicado.nombre} (ID: {menu_duplicado.id}) para {fecha_duplicado}")
        
        # 8. Probar consulta de historial
        print("\n8. 📚 Probando Historial de Menús...")
        menus_historial = db.query(MenuDiaRestructured).order_by(MenuDiaRestructured.fecha.desc()).limit(5).all()
        
        print(f"   📊 Total menús en historial: {len(menus_historial)}")
        for menu in menus_historial:
            estado_icon = "✅" if menu.estado == "ACTIVE" else "📝" if menu.estado == "DRAFT" else "❌"
            print(f"   {estado_icon} {menu.fecha} - {menu.nombre} (${menu.precio:,.0f} COP)")
        
        print("\n" + "=" * 60)
        print("🎉 ¡Todas las pruebas completadas exitosamente!")
        print("✅ Sistema de menús funcionando correctamente")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en el sistema: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = test_menu_system()
    if not success:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores anteriores.")
        sys.exit(1)
    else:
        print("\n✅ Todas las pruebas pasaron correctamente.")
