#!/usr/bin/env python3
"""
Script para limpiar menús usando la configuración de la aplicación
Intenta diferentes configuraciones de base de datos
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def intentar_conexiones():
    """Intentar diferentes configuraciones de conexión a la base de datos"""
    
    configuraciones = [
        # Configuración de la aplicación
        ("app.database", "Usando configuración de la aplicación"),
        # Configuraciones directas
        ("postgresql://postgres:postgres@localhost:5432/restaurante_pos", "PostgreSQL local"),
        ("postgresql://postgres:postgres@localhost:55432/restaurante_pos", "PostgreSQL Docker"),
        ("postgresql://postgres:postgres@host.docker.internal:5432/restaurante_pos", "PostgreSQL host.docker.internal"),
        ("sqlite:///./restaurante_pos.db", "SQLite local"),
    ]
    
    for config, descripcion in configuraciones:
        try:
            print(f"🔧 Intentando conexión: {descripcion}")
            
            if config == "app.database":
                # Usar configuración de la aplicación
                try:
                    from app.database import engine, SessionLocal
                    print(f"   ✅ Conexión exitosa usando configuración de la aplicación")
                    return engine, SessionLocal
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    continue
            else:
                # Usar configuración directa
                engine = create_engine(config)
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                
                # Probar la conexión
                with SessionLocal() as db:
                    db.execute(text("SELECT 1"))
                
                print(f"   ✅ Conexión exitosa: {descripcion}")
                return engine, SessionLocal
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    return None, None

def limpiar_menus_con_app():
    """Limpiar menús usando la configuración de la aplicación"""
    
    engine, SessionLocal = intentar_conexiones()
    if not engine or not SessionLocal:
        print("❌ No se pudo conectar a ninguna base de datos")
        return False
    
    try:
        with SessionLocal() as db:
            print("🧹 Iniciando limpieza usando configuración de la aplicación...")
            
            # 1. Verificar qué tablas existen
            print("\n📋 Verificando tablas existentes...")
            result = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%menu%'
                ORDER BY table_name
            """))
            tablas_menus = [row[0] for row in result.fetchall()]
            print(f"   🍽️ Tablas de menús encontradas: {tablas_menus}")
            
            # 2. Limpiar asociaciones primero
            print("\n📋 Eliminando asociaciones...")
            tablas_asociaciones = [t for t in tablas_menus if 'opcion' in t or 'plato' in t or 'item' in t]
            
            total_asociaciones = 0
            for tabla in tablas_asociaciones:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                    count_antes = result.scalar()
                    
                    if count_antes > 0:
                        result = db.execute(text(f"DELETE FROM {tabla}"))
                        eliminados = result.rowcount
                        print(f"   ✅ {tabla}: {eliminados} registros eliminados")
                        total_asociaciones += eliminados
                    else:
                        print(f"   ✅ {tabla}: 0 registros (ya estaba vacía)")
                        
                except Exception as e:
                    print(f"   ⚠️ Error en {tabla}: {e}")
            
            # 3. Limpiar menús
            print("\n🗑️ Eliminando menús...")
            tablas_menus_limpiar = [t for t in tablas_menus if t not in tablas_asociaciones]
            
            total_menus = 0
            for tabla in tablas_menus_limpiar:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                    count_antes = result.scalar()
                    
                    if count_antes > 0:
                        result = db.execute(text(f"DELETE FROM {tabla}"))
                        eliminados = result.rowcount
                        print(f"   ✅ {tabla}: {eliminados} registros eliminados")
                        total_menus += eliminados
                    else:
                        print(f"   ✅ {tabla}: 0 registros (ya estaba vacía)")
                        
                except Exception as e:
                    print(f"   ⚠️ Error en {tabla}: {e}")
            
            # 4. Verificar limpieza
            print("\n🔍 Verificando limpieza...")
            for tabla in tablas_menus:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                    count = result.scalar()
                    if count > 0:
                        print(f"   ⚠️ {tabla}: {count} registros restantes")
                    else:
                        print(f"   ✅ {tabla}: 0 registros (limpia)")
                except Exception as e:
                    print(f"   ⚠️ {tabla}: No se pudo verificar - {e}")
            
            # 5. Verificar platos
            print("\n📊 Verificando estado de platos...")
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
            
            # Confirmar cambios
            db.commit()
            print(f"\n✅ Limpieza completada!")
            print(f"📊 Total asociaciones eliminadas: {total_asociaciones}")
            print(f"📊 Total menús eliminados: {total_menus}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return False

if __name__ == "__main__":
    print("🧹 LIMPIADOR DE MENÚS CON CONFIGURACIÓN DE APP")
    print("=" * 60)
    
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
        
        if limpiar_menus_con_app():
            print("\n🎉 ¡Limpieza completada! Ahora puedes trabajar con los platos de forma limpia.")
        else:
            print("\n❌ Error durante la limpieza. Revisa los logs.")
    else:
        print("\n❌ Operación cancelada.")
