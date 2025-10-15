"""
Script para crear la tabla menus_dia si no existe
"""
import os
from sqlalchemy import create_engine, text
from app.config import settings

def create_menus_dia_table():
    """Crear la tabla menus_dia si no existe"""
    print("🔧 CREANDO TABLA menus_dia")
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
            
            if tabla_existe:
                print("✅ La tabla ya existe, no es necesario crearla")
                return
            
            # 2. Crear la tabla
            print("\n2️⃣ CREANDO TABLA menus_dia...")
            create_table_query = text("""
                CREATE TABLE menus_dia (
                    id SERIAL PRIMARY KEY,
                    fecha DATE NOT NULL UNIQUE,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    precio DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    estado VARCHAR(50),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            connection.execute(create_table_query)
            print("✅ Tabla menus_dia creada exitosamente")
            
            # 3. Crear índice en fecha
            print("\n3️⃣ CREANDO ÍNDICE EN FECHA...")
            create_index_query = text("""
                CREATE INDEX IF NOT EXISTS idx_menus_dia_fecha ON menus_dia(fecha);
            """)
            connection.execute(create_index_query)
            print("✅ Índice creado exitosamente")
            
            # 4. Insertar un menú de ejemplo
            print("\n4️⃣ INSERTANDO MENÚ DE EJEMPLO...")
            insert_menu_query = text("""
                INSERT INTO menus_dia (fecha, nombre, descripcion, precio, estado)
                VALUES (CURRENT_DATE, 'Menú de Ejemplo', 'Menú creado automáticamente', 15000.00, 'ACTIVE')
                ON CONFLICT (fecha) DO NOTHING;
            """)
            connection.execute(insert_menu_query)
            print("✅ Menú de ejemplo insertado")
            
            connection.commit()
            print("\n🎉 Tabla menus_dia creada y configurada exitosamente!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_menus_dia_table()