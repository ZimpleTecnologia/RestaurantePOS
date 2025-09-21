import os
from sqlalchemy import create_engine, text
from app.config import settings

def insert_sample_menu():
    """Insertar menú de ejemplo con la estructura correcta"""
    print("📋 Insertando menú de ejemplo...")
    print("=" * 50)
    
    db_url = settings.database_url
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as connection:
            # Insertar menú de ejemplo
            insert_query = text("""
                INSERT INTO menus_dia (fecha, nombre, descripcion, precio, estado)
                VALUES (CURRENT_DATE, 'Menú del Día', 'Menú especial del día', 15000.00, 'publicado')
                ON CONFLICT (fecha) DO UPDATE SET
                    nombre = EXCLUDED.nombre,
                    descripcion = EXCLUDED.descripcion,
                    precio = EXCLUDED.precio,
                    estado = EXCLUDED.estado;
            """)
            connection.execute(insert_query)
            connection.commit()
            print("✅ Menú de ejemplo insertado/actualizado")
            
            # Verificar que se insertó
            count_query = text("SELECT COUNT(*) FROM menus_dia;")
            count = connection.execute(count_query).scalar()
            print(f"📊 Total de menús: {count}")
            
            # Mostrar el menú insertado
            select_query = text("SELECT menu_id, fecha, nombre, precio, estado FROM menus_dia LIMIT 1;")
            result = connection.execute(select_query).fetchone()
            if result:
                print(f"📋 Menú: {result.nombre} (ID: {result.menu_id}, Fecha: {result.fecha}, Precio: {result.precio}, Estado: {result.estado})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    insert_sample_menu()


