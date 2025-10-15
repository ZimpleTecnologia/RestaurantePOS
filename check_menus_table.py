import os
from sqlalchemy import create_engine, text
from app.config import settings

def check_menus_table():
    """Verificar la estructura de la tabla menus_dia"""
    print("🔍 Verificando estructura de la tabla menus_dia...")
    print("=" * 60)
    
    db_url = settings.database_url
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as connection:
            # Verificar si la tabla existe
            check_table_query = text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'menus_dia'
                );
            """)
            table_exists = connection.execute(check_table_query).scalar()
            
            if table_exists:
                print("✅ Tabla 'menus_dia' existe")
                
                # Obtener estructura de la tabla
                print("\n📊 Estructura de la tabla:")
                structure_query = text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'menus_dia'
                    ORDER BY ordinal_position;
                """)
                columns = connection.execute(structure_query).fetchall()
                
                for col in columns:
                    print(f"   - {col.column_name} ({col.data_type}) - Nullable: {'YES' if col.is_nullable == 'YES' else 'NO'}")
                
                # Contar registros
                count_query = text("SELECT COUNT(*) FROM menus_dia;")
                count = connection.execute(count_query).scalar()
                print(f"\n📊 Registros en la tabla: {count}")
                
                # Mostrar algunos registros
                if count > 0:
                    print("\n📋 Primeros registros:")
                    sample_query = text("SELECT menu_id, fecha, nombre, precio, activo, publicado FROM menus_dia LIMIT 3;")
                    samples = connection.execute(sample_query).fetchall()
                    
                    for sample in samples:
                        print(f"   - ID: {sample.menu_id}, Fecha: {sample.fecha}, Nombre: {sample.nombre}, Precio: {sample.precio}")
                
            else:
                print("❌ Tabla 'menus_dia' no existe")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_menus_table()


