"""
Script para reestructurar el sistema de menús según los nuevos requerimientos
"""
import os
from sqlalchemy import create_engine, text
from app.config import settings

def restructure_menu_system():
    """Reestructurar el sistema de menús"""
    print("🔧 Reestructurando sistema de menús...")
    print("=" * 60)
    
    db_url = settings.database_url
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as connection:
            # 1. Crear tabla de categorías de platos variables
            print("📋 Creando tabla de categorías de platos variables...")
            create_categorias_query = text("""
                CREATE TABLE IF NOT EXISTS categorias_platos_variables (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL UNIQUE,
                    descripcion TEXT,
                    orden INTEGER DEFAULT 0,
                    activo BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            connection.execute(create_categorias_query)
            print("✅ Tabla categorias_platos_variables creada")
            
            # 2. Crear tabla de opciones de platos
            print("📋 Creando tabla de opciones de platos...")
            create_opciones_query = text("""
                CREATE TABLE IF NOT EXISTS opciones_platos (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    categoria_id INTEGER REFERENCES categorias_platos_variables(id),
                    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Fijo', 'Variable')),
                    precio DECIMAL(10,2) DEFAULT 0.00,
                    imagen_url VARCHAR(255),
                    activo BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            connection.execute(create_opciones_query)
            print("✅ Tabla opciones_platos creada")
            
            # 3. Crear tabla de menús del día con opciones
            print("📋 Creando tabla de menús del día con opciones...")
            create_menu_opciones_query = text("""
                CREATE TABLE IF NOT EXISTS menu_dia_opciones (
                    id SERIAL PRIMARY KEY,
                    menu_dia_id INTEGER REFERENCES menus_dia(id),
                    opcion_id INTEGER REFERENCES opciones_platos(id),
                    disponible BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            connection.execute(create_menu_opciones_query)
            print("✅ Tabla menu_dia_opciones creada")
            
            # 4. Insertar categorías por defecto
            print("📋 Insertando categorías por defecto...")
            insert_categorias_query = text("""
                INSERT INTO categorias_platos_variables (nombre, descripcion, orden) VALUES
                ('Principio', 'Platos de principio como verduras, frijoles, etc.', 1),
                ('Proteína', 'Platos de proteína como carnes, pollo, pescado, etc.', 2),
                ('Acompañamiento', 'Acompañamientos como arroz, papas, etc.', 3),
                ('Bebida', 'Bebidas del menú', 4),
                ('Postre', 'Postres del menú', 5)
                ON CONFLICT (nombre) DO NOTHING;
            """)
            connection.execute(insert_categorias_query)
            print("✅ Categorías por defecto insertadas")
            
            # 5. Insertar platos fijos por defecto
            print("📋 Insertando platos fijos por defecto...")
            insert_platos_fijos_query = text("""
                INSERT INTO opciones_platos (nombre, descripcion, tipo, precio, activo) VALUES
                ('Frijolada', 'Frijoles con carne y verduras', 'Fijo', 12000.00, TRUE),
                ('Chicharrón al Barril', 'Chicharrón de cerdo con yuca', 'Fijo', 15000.00, TRUE),
                ('Chuleta', 'Chuleta de cerdo a la plancha', 'Fijo', 18000.00, TRUE),
                ('Bandeja Paisa', 'Bandeja paisa completa', 'Fijo', 20000.00, TRUE)
                ON CONFLICT DO NOTHING;
            """)
            connection.execute(insert_platos_fijos_query)
            print("✅ Platos fijos por defecto insertados")
            
            # 6. Insertar platos variables por defecto
            print("📋 Insertando platos variables por defecto...")
            insert_platos_variables_query = text("""
                INSERT INTO opciones_platos (nombre, descripcion, categoria_id, tipo, precio, activo) VALUES
                ('Verduras a la Crema', 'Verduras cocidas en crema', 1, 'Variable', 8000.00, TRUE),
                ('Frijoles', 'Frijoles rojos con verduras', 1, 'Variable', 7000.00, TRUE),
                ('Pechuga a la Plancha', 'Pechuga de pollo a la plancha', 2, 'Variable', 12000.00, TRUE),
                ('Carne de Cerdo', 'Carne de cerdo guisada', 2, 'Variable', 14000.00, TRUE),
                ('Hígado Encebollado', 'Hígado de res con cebolla', 2, 'Variable', 13000.00, TRUE),
                ('Arroz Blanco', 'Arroz blanco cocido', 3, 'Variable', 3000.00, TRUE),
                ('Papas Fritas', 'Papas fritas caseras', 3, 'Variable', 4000.00, TRUE),
                ('Jugo de Naranja', 'Jugo natural de naranja', 4, 'Variable', 5000.00, TRUE),
                ('Limonada', 'Limonada natural', 4, 'Variable', 4000.00, TRUE),
                ('Flan', 'Flan de leche', 5, 'Variable', 6000.00, TRUE),
                ('Gelatina', 'Gelatina de frutas', 5, 'Variable', 4000.00, TRUE)
                ON CONFLICT DO NOTHING;
            """)
            connection.execute(insert_platos_variables_query)
            print("✅ Platos variables por defecto insertados")
            
            connection.commit()
            print("\n🎉 Sistema de menús reestructurado exitosamente!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    restructure_menu_system()


