#!/usr/bin/env python3
"""
Script para verificar que todas las tablas del Sistema POS existen en la base de datos
"""
import sys
import os
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from app.database import get_db, create_tables, engine
from app.models import *
from app.config import settings

def get_expected_tables():
    """Obtener lista de todas las tablas esperadas según los modelos"""
    expected_tables = [
        # Tablas principales
        "users",
        "categories", 
        "subcategories",
        "products",
        "sales",
        "sale_items",
        "payment_methods",
        "customers",
        "credits",
        "payments",
        "suppliers",
        "purchases",
        "purchase_items",
        "locations",
        "tables",
        "inventory_movements",
        "recipes",
        "recipe_items",
        "system_settings",
        "orders",
        "order_items"
    ]
    return expected_tables

def get_expected_enums():
    """Obtener lista de todos los enums esperados"""
    expected_enums = [
        "userrole",
        "producttype", 
        "purchasestatus",
        "locationtype",
        "tablestatus"
    ]
    return expected_enums

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print("🔄 Verificando conexión a la base de datos...")
    
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Conexión a la base de datos establecida")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def get_existing_tables():
    """Obtener lista de tablas existentes en la base de datos"""
    print("\n📋 Obteniendo tablas existentes...")
    
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"✅ Se encontraron {len(existing_tables)} tablas en la base de datos")
        return existing_tables
    except Exception as e:
        print(f"❌ Error obteniendo tablas: {e}")
        return []

def get_existing_enums():
    """Obtener lista de enums existentes en la base de datos"""
    print("\n📋 Obteniendo enums existentes...")
    
    try:
        db = next(get_db())
        result = db.execute(text("""
            SELECT t.typname 
            FROM pg_type t 
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace 
            WHERE t.typtype = 'e' 
            AND n.nspname = 'public'
        """))
        existing_enums = [row[0] for row in result]
        db.close()
        print(f"✅ Se encontraron {len(existing_enums)} enums en la base de datos")
        return existing_enums
    except Exception as e:
        print(f"❌ Error obteniendo enums: {e}")
        return []

def check_tables():
    """Verificar que todas las tablas esperadas existen"""
    print("\n🔍 Verificando tablas...")
    
    expected_tables = get_expected_tables()
    existing_tables = get_existing_tables()
    
    missing_tables = []
    existing_expected_tables = []
    
    for table in expected_tables:
        if table in existing_tables:
            existing_expected_tables.append(table)
            print(f"✅ Tabla '{table}' existe")
        else:
            missing_tables.append(table)
            print(f"❌ Tabla '{table}' NO existe")
    
    # Verificar tablas extra
    extra_tables = [table for table in existing_tables if table not in expected_tables]
    
    print(f"\n📊 Resumen de tablas:")
    print(f"   ✅ Tablas esperadas que existen: {len(existing_expected_tables)}/{len(expected_tables)}")
    print(f"   ❌ Tablas faltantes: {len(missing_tables)}")
    print(f"   🔍 Tablas extra encontradas: {len(extra_tables)}")
    
    if extra_tables:
        print(f"   📝 Tablas extra: {', '.join(extra_tables)}")
    
    return missing_tables, extra_tables

def check_enums():
    """Verificar que todos los enums esperados existen"""
    print("\n🔍 Verificando enums...")
    
    expected_enums = get_expected_enums()
    existing_enums = get_existing_enums()
    
    missing_enums = []
    existing_expected_enums = []
    
    for enum in expected_enums:
        if enum in existing_enums:
            existing_expected_enums.append(enum)
            print(f"✅ Enum '{enum}' existe")
        else:
            missing_enums.append(enum)
            print(f"❌ Enum '{enum}' NO existe")
    
    # Verificar enums extra
    extra_enums = [enum for enum in existing_enums if enum not in expected_enums]
    
    print(f"\n📊 Resumen de enums:")
    print(f"   ✅ Enums esperados que existen: {len(existing_expected_enums)}/{len(expected_enums)}")
    print(f"   ❌ Enums faltantes: {len(missing_enums)}")
    print(f"   🔍 Enums extra encontrados: {len(extra_enums)}")
    
    if extra_enums:
        print(f"   📝 Enums extra: {', '.join(extra_enums)}")
    
    return missing_enums, extra_enums

def check_table_columns(table_name):
    """Verificar columnas de una tabla específica"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        print(f"   📋 Columnas en '{table_name}': {len(columns)}")
        for col in columns:
            print(f"      - {col['name']}: {col['type']}")
    except Exception as e:
        print(f"   ❌ Error verificando columnas de '{table_name}': {e}")

def check_table_structure():
    """Verificar estructura de tablas principales"""
    print("\n🔍 Verificando estructura de tablas principales...")
    
    main_tables = ["users", "products", "sales", "customers", "orders"]
    existing_tables = get_existing_tables()
    
    for table in main_tables:
        if table in existing_tables:
            print(f"\n📋 Estructura de tabla '{table}':")
            check_table_columns(table)
        else:
            print(f"\n❌ Tabla '{table}' no existe para verificar estructura")

def create_missing_tables():
    """Crear tablas faltantes"""
    print("\n🔧 Creando tablas faltantes...")
    
    try:
        create_tables()
        print("✅ Tablas creadas/verificadas")
        return True
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

def get_table_counts():
    """Obtener conteo de registros en cada tabla"""
    print("\n📊 Conteo de registros por tabla:")
    
    expected_tables = get_expected_tables()
    existing_tables = get_existing_tables()
    
    db = next(get_db())
    
    try:
        for table in expected_tables:
            if table in existing_tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"   📋 {table}: {count} registros")
                except Exception as e:
                    print(f"   ❌ Error contando {table}: {e}")
            else:
                print(f"   ❌ {table}: tabla no existe")
    finally:
        db.close()

def main():
    """Función principal"""
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE TABLAS - SISTEMA POS")
    print("=" * 70)
    print(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar conexión
    if not check_database_connection():
        print("❌ No se puede continuar sin conexión a la base de datos")
        sys.exit(1)
    
    # Verificar tablas
    missing_tables, extra_tables = check_tables()
    
    # Verificar enums
    missing_enums, extra_enums = check_enums()
    
    # Verificar estructura de tablas principales
    check_table_structure()
    
    # Obtener conteos
    get_table_counts()
    
    # Crear tablas faltantes si es necesario
    if missing_tables:
        print(f"\n⚠️  Se encontraron {len(missing_tables)} tablas faltantes")
        response = input("¿Quieres crear las tablas faltantes? (sí/no): ").lower().strip()
        if response in ['sí', 'si', 'yes', 'y', 's']:
            if create_missing_tables():
                print("✅ Tablas faltantes creadas")
                # Verificar nuevamente
                missing_tables_after, _ = check_tables()
                if not missing_tables_after:
                    print("🎉 Todas las tablas están ahora presentes")
                else:
                    print(f"⚠️  Aún faltan {len(missing_tables_after)} tablas")
            else:
                print("❌ Error creando tablas faltantes")
        else:
            print("ℹ️  No se crearon tablas faltantes")
    else:
        print("\n🎉 Todas las tablas esperadas están presentes")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📋 RESUMEN FINAL")
    print("=" * 70)
    print(f"✅ Tablas esperadas: {len(get_expected_tables())}")
    print(f"✅ Enums esperados: {len(get_expected_enums())}")
    print(f"❌ Tablas faltantes: {len(missing_tables)}")
    print(f"❌ Enums faltantes: {len(missing_enums)}")
    print(f"🔍 Tablas extra: {len(extra_tables)}")
    print(f"🔍 Enums extra: {len(extra_enums)}")
    
    if not missing_tables and not missing_enums:
        print("\n🎉 ¡Base de datos completamente configurada!")
    else:
        print("\n⚠️  Se encontraron elementos faltantes")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
