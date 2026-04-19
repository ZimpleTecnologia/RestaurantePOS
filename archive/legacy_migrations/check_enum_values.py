import os
from sqlalchemy import create_engine, text
from app.config import settings

def check_enum_values():
    """Verificar los valores del ENUM menustatus"""
    print("🔍 Verificando valores del ENUM menustatus...")
    print("=" * 60)
    
    db_url = settings.database_url
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as connection:
            # Obtener valores del ENUM
            enum_query = text("""
                SELECT unnest(enum_range(NULL::menustatus)) as enum_value;
            """)
            enum_values = connection.execute(enum_query).fetchall()
            
            print("📋 Valores del ENUM menustatus:")
            for value in enum_values:
                print(f"   - '{value.enum_value}'")
            
            # Probar insertar con un valor válido
            print("\n📋 Probando inserción con valor válido...")
            insert_query = text("""
                INSERT INTO menus_dia (fecha, nombre, descripcion, precio, estado)
                VALUES (CURRENT_DATE, 'Menú del Día', 'Menú especial del día', 15000.00, 'ACTIVE')
                ON CONFLICT (fecha) DO UPDATE SET
                    nombre = EXCLUDED.nombre,
                    descripcion = EXCLUDED.descripcion,
                    precio = EXCLUDED.precio,
                    estado = EXCLUDED.estado;
            """)
            connection.execute(insert_query)
            connection.commit()
            print("✅ Menú insertado exitosamente con estado 'activo'")
            
            # Verificar que se insertó
            count_query = text("SELECT COUNT(*) FROM menus_dia;")
            count = connection.execute(count_query).scalar()
            print(f"📊 Total de menús: {count}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_enum_values()
