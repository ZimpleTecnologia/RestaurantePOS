import os
from sqlalchemy import create_engine, text
from app.config import settings

def check_table_structure():
    """Verificar la estructura real de la tabla menus_dia"""
    print("🔍 Verificando estructura de la tabla menus_dia...")
    print("=" * 60)
    
    db_url = settings.database_url
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as connection:
            # Obtener información detallada de la tabla
            structure_query = text("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    column_default,
                    ordinal_position
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'menus_dia'
                ORDER BY ordinal_position;
            """)
            columns = connection.execute(structure_query).fetchall()
            
            print("📊 Estructura de la tabla menus_dia:")
            for col in columns:
                print(f"   {col.ordinal_position}. {col.column_name} ({col.data_type}) - Nullable: {'YES' if col.is_nullable == 'YES' else 'NO'}")
            
            # Verificar si hay datos
            count_query = text("SELECT COUNT(*) FROM menus_dia;")
            count = connection.execute(count_query).scalar()
            print(f"\n📊 Total de registros: {count}")
            
            if count > 0:
                # Mostrar un registro de ejemplo
                sample_query = text("SELECT * FROM menus_dia LIMIT 1;")
                sample = connection.execute(sample_query).fetchone()
                print(f"\n📋 Registro de ejemplo:")
                for col in columns:
                    value = getattr(sample, col.column_name, 'N/A')
                    print(f"   {col.column_name}: {value}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_table_structure()