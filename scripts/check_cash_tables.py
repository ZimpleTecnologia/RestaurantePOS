#!/usr/bin/env python3
"""
Script para verificar la estructura real de las tablas de caja
"""
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.database import get_db, engine

def check_cash_tables_structure():
    """Verificar la estructura real de las tablas de caja"""
    print("🔍 Verificando estructura de las tablas de caja...")
    
    db = next(get_db())
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        cash_tables = ['cash_registers', 'cash_sessions', 'cash_movements']
        
        for table in cash_tables:
            print(f"\n📋 Tabla: {table}")
            if table in tables:
                columns = inspector.get_columns(table)
                print(f"✅ Existe - Columnas:")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']} {'(NOT NULL)' if not column['nullable'] else ''}")
                
                # Verificar registros
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"📊 Registros: {count}")
                
                if count > 0:
                    result = db.execute(text(f"SELECT * FROM {table} LIMIT 2"))
                    rows = result.fetchall()
                    print(f"📄 Ejemplos:")
                    for row in rows:
                        print(f"  {dict(row)}")
            else:
                print(f"❌ No existe")

    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE TABLAS DE CAJA")
    print("=" * 60)
    
    check_cash_tables_structure()
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico completado")

if __name__ == "__main__":
    main()
