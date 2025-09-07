#!/usr/bin/env python3
"""
Script para verificar la estructura real de la tabla sales
"""
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.database import get_db, engine

def check_sales_table_structure():
    """Verificar la estructura real de la tabla sales"""
    print("🔍 Verificando estructura de la tabla 'sales'...")
    
    db = next(get_db())
    
    try:
        # Verificar si la tabla existe
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'sales' not in tables:
            print("❌ La tabla 'sales' no existe")
            return
        
        print("✅ La tabla 'sales' existe")
        
        # Obtener columnas de la tabla sales
        columns = inspector.get_columns('sales')
        
        print("\n📋 Columnas existentes en la tabla 'sales':")
        for column in columns:
            print(f"  - {column['name']}: {column['type']}")
        
        # Verificar si hay datos
        result = db.execute(text("SELECT COUNT(*) FROM sales"))
        count = result.scalar()
        print(f"\n📊 Registros en la tabla 'sales': {count}")
        
        if count > 0:
            # Mostrar algunos registros de ejemplo
            result = db.execute(text("SELECT * FROM sales LIMIT 3"))
            rows = result.fetchall()
            
            print("\n📄 Ejemplos de registros:")
            for row in rows:
                print(f"  {dict(row)}")
        
    except Exception as e:
        print(f"❌ Error verificando tabla sales: {e}")
        import traceback
        traceback.print_exc()

def check_related_tables():
    """Verificar tablas relacionadas"""
    print("\n🔗 Verificando tablas relacionadas...")
    
    db = next(get_db())
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        related_tables = ['sale_items', 'payment_methods', 'customers', 'users', 'locations', 'tables']
        
        for table in related_tables:
            if table in tables:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"✅ {table}: {count} registros")
            else:
                print(f"❌ {table}: No existe")

    except Exception as e:
        print(f"❌ Error verificando tablas relacionadas: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE LA TABLA SALES")
    print("=" * 60)
    
    check_sales_table_structure()
    check_related_tables()
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico completado")

if __name__ == "__main__":
    main()
