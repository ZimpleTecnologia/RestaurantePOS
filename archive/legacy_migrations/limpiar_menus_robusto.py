#!/usr/bin/env python3
"""
Script robusto para limpiar todos los menús y sus asociaciones
Maneja errores de transacción y verifica tablas existentes
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Configuración de base de datos
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/restaurante_pos"

def conectar_base_datos():
    """Conectar a la base de datos con manejo de errores"""
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None, None

def verificar_tablas_existentes(engine):
    """Verificar qué tablas existen en la base de datos"""
    try:
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        print(f"📋 Tablas encontradas: {len(tablas)}")
        
        # Filtrar tablas relacionadas con menús
        tablas_menus = [t for t in tablas if 'menu' in t.lower()]
        print(f"🍽️ Tablas de menús: {tablas_menus}")
        
        return tablas_menus
    except Exception as e:
        print(f"⚠️ Error verificando tablas: {e}")
        return []

def limpiar_tabla_segura(db, nombre_tabla, descripcion):
    """Limpiar una tabla de forma segura con manejo de errores"""
    try:
        # Verificar si la tabla existe
        result = db.execute(text(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{nombre_tabla}'"))
        existe = result.scalar() > 0
        
        if not existe:
            print(f"   ⚠️ Tabla '{nombre_tabla}' no existe, saltando...")
            return 0
        
        # Contar registros antes de eliminar
        result = db.execute(text(f"SELECT COUNT(*) FROM {nombre_tabla}"))
        count_antes = result.scalar()
        
        if count_antes == 0:
            print(f"   ✅ {descripcion}: 0 registros (ya estaba vacía)")
            return 0
        
        # Eliminar registros
        result = db.execute(text(f"DELETE FROM {nombre_tabla}"))
        count_eliminados = result.rowcount
        
        print(f"   ✅ {descripcion}: {count_eliminados} registros eliminados")
        return count_eliminados
        
    except Exception as e:
        print(f"   ❌ Error limpiando {nombre_tabla}: {e}")
        return 0

def limpiar_menus_robusto():
    """Limpieza robusta de menús con manejo de errores"""
    
    engine, SessionLocal = conectar_base_datos()
    if not engine or not SessionLocal:
        return False
    
    try:
        with SessionLocal() as db:
            print("🧹 Iniciando limpieza robusta de menús...")
            
            # Verificar tablas existentes
            tablas_menus = verificar_tablas_existentes(engine)
            
            # 1. Limpiar asociaciones primero (orden importante)
            print("\n📋 Eliminando asociaciones de menús con opciones...")
            
            # Lista de tablas de asociaciones a limpiar
            tablas_asociaciones = [
                ("menu_dia_opciones", "Asociaciones menu_dia_opciones"),
                ("menu_opciones", "Asociaciones menu_opciones"),
                ("menu_platos", "Asociaciones menu_platos"),
                ("menu_items", "Asociaciones menu_items")
            ]
            
            total_asociaciones = 0
            for tabla, descripcion in tablas_asociaciones:
                eliminados = limpiar_tabla_segura(db, tabla, descripcion)
                total_asociaciones += eliminados
            
            # 2. Limpiar menús
            print("\n🗑️ Eliminando todos los menús...")
            
            # Lista de tablas de menús a limpiar
            tablas_menus_limpiar = [
                ("menu_dia_restructured", "Menús restructurados"),
                ("menu_dia", "Menús del día"),
                ("menus", "Menús generales"),
                ("menu_hoy", "Menús de hoy")
            ]
            
            total_menus = 0
            for tabla, descripcion in tablas_menus_limpiar:
                eliminados = limpiar_tabla_segura(db, tabla, descripcion)
                total_menus += eliminados
            
            # 3. Verificar limpieza
            print("\n🔍 Verificando limpieza...")
            
            # Verificar asociaciones restantes
            for tabla, descripcion in tablas_asociaciones:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                    count = result.scalar()
                    if count > 0:
                        print(f"   ⚠️ {descripcion}: {count} registros restantes")
                    else:
                        print(f"   ✅ {descripcion}: 0 registros (limpia)")
                except:
                    print(f"   ⚠️ {descripcion}: No se pudo verificar")
            
            # Verificar menús restantes
            for tabla, descripcion in tablas_menus_limpiar:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                    count = result.scalar()
                    if count > 0:
                        print(f"   ⚠️ {descripcion}: {count} registros restantes")
                    else:
                        print(f"   ✅ {descripcion}: 0 registros (limpia)")
                except:
                    print(f"   ⚠️ {descripcion}: No se pudo verificar")
            
            # Confirmar cambios
            db.commit()
            print(f"\n✅ Limpieza completada!")
            print(f"📊 Total asociaciones eliminadas: {total_asociaciones}")
            print(f"📊 Total menús eliminados: {total_menus}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return False

def verificar_estado_final():
    """Verificar el estado final después de la limpieza"""
    
    engine, SessionLocal = conectar_base_datos()
    if not engine or not SessionLocal:
        return
    
    try:
        with SessionLocal() as db:
            print("\n📊 Estado final del sistema:")
            
            # Verificar platos
            try:
                result = db.execute(text("SELECT COUNT(*) FROM opciones_platos"))
                total_platos = result.scalar()
                print(f"   🍽️ Total de platos: {total_platos}")
                
                result = db.execute(text("SELECT COUNT(*) FROM opciones_platos WHERE activo = true"))
                platos_activos = result.scalar()
                print(f"   ✅ Platos activos: {platos_activos}")
                
                result = db.execute(text("SELECT COUNT(*) FROM opciones_platos WHERE activo = false"))
                platos_inactivos = result.scalar()
                print(f"   ❌ Platos inactivos: {platos_inactivos}")
                
            except Exception as e:
                print(f"   ⚠️ Error verificando platos: {e}")
            
            # Verificar categorías
            try:
                result = db.execute(text("SELECT COUNT(*) FROM categorias_platos_variables"))
                total_categorias = result.scalar()
                print(f"   🏷️ Total de categorías: {total_categorias}")
                
            except Exception as e:
                print(f"   ⚠️ Error verificando categorías: {e}")
            
            # Verificar menús restantes
            print("\n🔍 Verificando menús restantes:")
            tablas_verificar = ["menu_dia_restructured", "menu_dia", "menus", "menu_hoy"]
            
            for tabla in tablas_verificar:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                    count = result.scalar()
                    if count > 0:
                        print(f"   ⚠️ {tabla}: {count} registros restantes")
                    else:
                        print(f"   ✅ {tabla}: 0 registros (limpia)")
                except:
                    print(f"   ⚠️ {tabla}: No existe o no se pudo verificar")
                    
    except Exception as e:
        print(f"❌ Error verificando estado final: {e}")

if __name__ == "__main__":
    print("🧹 LIMPIADOR ROBUSTO DE MENÚS")
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
        print("\n🚀 Iniciando limpieza robusta...")
        
        if limpiar_menus_robusto():
            verificar_estado_final()
            print("\n🎉 ¡Limpieza completada! Ahora puedes trabajar con los platos de forma limpia.")
        else:
            print("\n❌ Error durante la limpieza. Revisa los logs.")
    else:
        print("\n❌ Operación cancelada.")

