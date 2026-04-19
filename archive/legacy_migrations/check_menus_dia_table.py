"""
Script para verificar la estructura de la tabla menus_dia
"""
import os
from sqlalchemy import create_engine, text
from app.config import settings

def check_menus_dia_table():
    """Verificar la estructura de la tabla menus_dia"""
    print("🔍 VERIFICANDO ESTRUCTURA DE LA TABLA menus_dia")
    print("=" * 70)
    
    db_url = settings.database_url
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as connection:
            # 1. Verificar si la tabla existe
            print("\n1️⃣ VERIFICANDO EXISTENCIA DE LA TABLA...")
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'menus_dia'
                );
            """))
            tabla_existe = result.fetchone()[0]
            print(f"📋 Tabla menus_dia: {'✅ Existe' if tabla_existe else '❌ No existe'}")
            
            if not tabla_existe:
                print("❌ La tabla menus_dia no existe. Necesitamos crearla.")
                return
            
            # 2. Verificar estructura de la tabla
            print("\n2️⃣ VERIFICANDO ESTRUCTURA DE LA TABLA...")
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'menus_dia'
                ORDER BY ordinal_position;
            """))
            columnas = result.fetchall()
            print(f"📋 Columnas encontradas: {len(columnas)}")
            for col in columnas:
                print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # 3. Verificar si tiene la columna id
            columnas_nombres = [col[0] for col in columnas]
            if 'id' in columnas_nombres:
                print("✅ Columna 'id' encontrada")
            else:
                print("❌ Columna 'id' NO encontrada")
                print("   Columnas disponibles:", columnas_nombres)
            
            # 4. Verificar datos en la tabla
            print("\n3️⃣ VERIFICANDO DATOS EN LA TABLA...")
            result = connection.execute(text("SELECT COUNT(*) FROM menus_dia"))
            count = result.fetchone()[0]
            print(f"📋 Registros en menus_dia: {count}")
            
            if count > 0:
                result = connection.execute(text("SELECT * FROM menus_dia LIMIT 3"))
                registros = result.fetchall()
                print("📋 Primeros registros:")
                for reg in registros:
                    print(f"   - {reg}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_menus_dia_table()


