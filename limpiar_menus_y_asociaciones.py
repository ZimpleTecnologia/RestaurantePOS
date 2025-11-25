#!/usr/bin/env python3
"""
Script para limpiar todos los menús y sus asociaciones
Permite trabajar con platos de forma limpia
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.database import get_database_url
    from app.models.menu_restructured import MenuDiaRestructured, MenuDiaOpcion
    from app.models.menu_unified import MenuDia, MenuOpcion
    from app.models.restaurant_menu import MenuDia as RestaurantMenuDia, MenuDiaOpcion as RestaurantMenuDiaOpcion
    from app.models.carta_restaurante import MenuDia as CartaMenuDia, MenuOpcion as CartaMenuOpcion
except ImportError as e:
    print(f"❌ Error importando modelos: {e}")
    print("🔧 Intentando conexión directa a la base de datos...")
    
    # Configuración directa de la base de datos
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/restaurante_pos"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def limpiar_menus_y_asociaciones():
    """Eliminar todos los menús y sus asociaciones"""
    
    try:
        # Crear sesión de base de datos
        if 'SessionLocal' not in locals():
            from app.database import SessionLocal
        
        with SessionLocal() as db:
            print("🧹 Iniciando limpieza de menús y asociaciones...")
            
            # 1. Eliminar asociaciones de menús con opciones (tablas de relación)
            print("\n📋 Eliminando asociaciones de menús con opciones...")
            
            # Limpiar tabla menu_dia_opciones (menu_restructured)
            try:
                result = db.execute(text("DELETE FROM menu_dia_opciones"))
                print(f"   ✅ Eliminadas {result.rowcount} asociaciones de menu_dia_opciones")
            except Exception as e:
                print(f"   ⚠️  Error limpiando menu_dia_opciones: {e}")
            
            # Limpiar tabla menu_opciones (menu_unified)
            try:
                result = db.execute(text("DELETE FROM menu_opciones"))
                print(f"   ✅ Eliminadas {result.rowcount} asociaciones de menu_opciones")
            except Exception as e:
                print(f"   ⚠️  Error limpiando menu_opciones: {e}")
            
            # Limpiar tabla menu_dia_opciones (restaurant_menu)
            try:
                result = db.execute(text("DELETE FROM menu_dia_opciones"))
                print(f"   ✅ Eliminadas {result.rowcount} asociaciones de restaurant_menu menu_dia_opciones")
            except Exception as e:
                print(f"   ⚠️  Error limpiando restaurant_menu menu_dia_opciones: {e}")
            
            # Limpiar tabla menu_opciones (carta_restaurante)
            try:
                result = db.execute(text("DELETE FROM menu_opciones"))
                print(f"   ✅ Eliminadas {result.rowcount} asociaciones de carta_restaurante menu_opciones")
            except Exception as e:
                print(f"   ⚠️  Error limpiando carta_restaurante menu_opciones: {e}")
            
            # 2. Eliminar todos los menús
            print("\n🗑️ Eliminando todos los menús...")
            
            # Eliminar menús de menu_restructured
            try:
                result = db.execute(text("DELETE FROM menu_dia_restructured"))
                print(f"   ✅ Eliminados {result.rowcount} menús de menu_dia_restructured")
            except Exception as e:
                print(f"   ⚠️  Error eliminando menu_dia_restructured: {e}")
            
            # Eliminar menús de menu_unified
            try:
                result = db.execute(text("DELETE FROM menu_dia"))
                print(f"   ✅ Eliminados {result.rowcount} menús de menu_dia (unified)")
            except Exception as e:
                print(f"   ⚠️  Error eliminando menu_dia (unified): {e}")
            
            # Eliminar menús de restaurant_menu
            try:
                result = db.execute(text("DELETE FROM menu_dia"))
                print(f"   ✅ Eliminados {result.rowcount} menús de restaurant_menu menu_dia")
            except Exception as e:
                print(f"   ⚠️  Error eliminando restaurant_menu menu_dia: {e}")
            
            # Eliminar menús de carta_restaurante
            try:
                result = db.execute(text("DELETE FROM menu_dia"))
                print(f"   ✅ Eliminados {result.rowcount} menús de carta_restaurante menu_dia")
            except Exception as e:
                print(f"   ⚠️  Error eliminando carta_restaurante menu_dia: {e}")
            
            # 3. Verificar que no queden asociaciones
            print("\n🔍 Verificando que no queden asociaciones...")
            
            try:
                # Verificar menu_dia_opciones
                result = db.execute(text("SELECT COUNT(*) FROM menu_dia_opciones"))
                count = result.scalar()
                print(f"   📊 Asociaciones restantes en menu_dia_opciones: {count}")
                
                # Verificar menu_opciones
                result = db.execute(text("SELECT COUNT(*) FROM menu_opciones"))
                count = result.scalar()
                print(f"   📊 Asociaciones restantes en menu_opciones: {count}")
                
            except Exception as e:
                print(f"   ⚠️  Error verificando asociaciones: {e}")
            
            # 4. Verificar que no queden menús
            print("\n🔍 Verificando que no queden menús...")
            
            try:
                # Verificar menu_dia_restructured
                result = db.execute(text("SELECT COUNT(*) FROM menu_dia_restructured"))
                count = result.scalar()
                print(f"   📊 Menús restantes en menu_dia_restructured: {count}")
                
                # Verificar menu_dia (unified)
                result = db.execute(text("SELECT COUNT(*) FROM menu_dia"))
                count = result.scalar()
                print(f"   📊 Menús restantes en menu_dia (unified): {count}")
                
            except Exception as e:
                print(f"   ⚠️  Error verificando menús: {e}")
            
            # Confirmar cambios
            db.commit()
            print("\n✅ Limpieza completada exitosamente!")
            print("🎯 Ahora puedes trabajar con los platos de forma limpia")
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return False
    
    return True

def verificar_estado_platos():
    """Verificar el estado actual de los platos después de la limpieza"""
    
    try:
        with SessionLocal() as db:
            print("\n📊 Estado actual de los platos:")
            
            # Verificar opciones_platos
            try:
                result = db.execute(text("SELECT COUNT(*) FROM opciones_platos"))
                total_platos = result.scalar()
                print(f"   🍽️ Total de platos: {total_platos}")
                
                # Platos activos
                result = db.execute(text("SELECT COUNT(*) FROM opciones_platos WHERE activo = true"))
                platos_activos = result.scalar()
                print(f"   ✅ Platos activos: {platos_activos}")
                
                # Platos inactivos
                result = db.execute(text("SELECT COUNT(*) FROM opciones_platos WHERE activo = false"))
                platos_inactivos = result.scalar()
                print(f"   ❌ Platos inactivos: {platos_inactivos}")
                
            except Exception as e:
                print(f"   ⚠️  Error verificando platos: {e}")
            
            # Verificar categorías
            try:
                result = db.execute(text("SELECT COUNT(*) FROM categorias_platos_variables"))
                total_categorias = result.scalar()
                print(f"   🏷️ Total de categorías: {total_categorias}")
                
            except Exception as e:
                print(f"   ⚠️  Error verificando categorías: {e}")
                
    except Exception as e:
        print(f"❌ Error verificando estado: {e}")

if __name__ == "__main__":
    print("🧹 LIMPIADOR DE MENÚS Y ASOCIACIONES")
    print("=" * 50)
    
    # Confirmar acción
    print("⚠️  ADVERTENCIA: Este script eliminará TODOS los menús y sus asociaciones.")
    print("📋 Esto incluye:")
    print("   - Todos los menús del día")
    print("   - Todas las asociaciones plato-menú")
    print("   - Datos de menús en todas las tablas")
    print("\n✅ Los platos (opciones_platos) NO se eliminarán")
    print("✅ Las categorías NO se eliminarán")
    
    respuesta = input("\n¿Continuar con la limpieza? (sí/no): ").lower().strip()
    
    if respuesta in ['sí', 'si', 's', 'yes', 'y']:
        print("\n🚀 Iniciando limpieza...")
        
        if limpiar_menus_y_asociaciones():
            verificar_estado_platos()
            print("\n🎉 ¡Limpieza completada! Ahora puedes trabajar con los platos de forma limpia.")
        else:
            print("\n❌ Error durante la limpieza. Revisa los logs.")
    else:
        print("\n❌ Operación cancelada.")

