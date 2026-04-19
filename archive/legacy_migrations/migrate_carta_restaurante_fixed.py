#!/usr/bin/env python3
"""
Script de migración corregido para Carta Restaurante
"""

import logging
from sqlalchemy import create_engine, text
from app.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_engine_connection():
    """Crear conexión a la base de datos"""
    engine = create_engine(settings.database_url)
    return engine

def check_menus_dia_structure(engine):
    """Verificar estructura de menus_dia existente"""
    logger.info("🔄 Verificando estructura de menus_dia...")
    
    with engine.connect() as conn:
        try:
            # Verificar columnas existentes
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'menus_dia' 
                ORDER BY ordinal_position
            """))
            
            columns = [row[0] for row in result]
            logger.info(f"📋 Columnas existentes en menus_dia: {columns}")
            
            # Verificar si tiene menu_id o id
            has_menu_id = 'menu_id' in columns
            has_id = 'id' in columns
            
            logger.info(f"✅ ¿Tiene menu_id?: {has_menu_id}")
            logger.info(f"✅ ¿Tiene id?: {has_id}")
            
            return has_menu_id, has_id, columns
            
        except Exception as e:
            logger.error(f"Error verificando estructura: {e}")
            return False, False, []

def create_carta_restaurante_table(engine):
    """Crear tabla carta_restaurante"""
    logger.info("🔄 Creando tabla carta_restaurante...")
    
    with engine.connect() as conn:
        try:
            # Verificar si la tabla ya existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'carta_restaurante'
                )
            """))
            
            table_exists = result.scalar()
            
            if not table_exists:
                conn.execute(text("""
                    CREATE TABLE carta_restaurante (
                        producto_id SERIAL PRIMARY KEY,
                        nombre VARCHAR(100) NOT NULL,
                        descripcion TEXT,
                        precio_base DECIMAL(10,2) NOT NULL,
                        tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Fijo', 'Variable')),
                        activo BOOLEAN DEFAULT TRUE,
                        categoria VARCHAR(50),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                
                # Crear índices
                conn.execute(text("""
                    CREATE INDEX idx_carta_restaurante_tipo ON carta_restaurante(tipo)
                """))
                
                conn.execute(text("""
                    CREATE INDEX idx_carta_restaurante_activo ON carta_restaurante(activo)
                """))
                
                conn.execute(text("""
                    CREATE INDEX idx_carta_restaurante_categoria ON carta_restaurante(categoria)
                """))
                
                conn.commit()
                logger.info("✅ Tabla carta_restaurante creada")
            else:
                logger.info("ℹ️ Tabla carta_restaurante ya existe")
                
        except Exception as e:
            logger.error(f"Error creando carta_restaurante: {e}")
            raise

def create_menus_dia_carta_table(engine):
    """Crear tabla menus_dia_carta para el sistema de carta restaurante"""
    logger.info("🔄 Creando tabla menus_dia_carta...")
    
    with engine.connect() as conn:
        try:
            # Verificar si la tabla ya existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'menus_dia_carta'
                )
            """))
            
            table_exists = result.scalar()
            
            if not table_exists:
                conn.execute(text("""
                    CREATE TABLE menus_dia_carta (
                        menu_id SERIAL PRIMARY KEY,
                        fecha VARCHAR(10) NOT NULL UNIQUE,
                        nombre VARCHAR(100) NOT NULL,
                        precio DECIMAL(10,2) NOT NULL,
                        descripcion TEXT,
                        activo BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                
                # Crear índices
                conn.execute(text("""
                    CREATE INDEX idx_menus_dia_carta_fecha ON menus_dia_carta(fecha)
                """))
                
                conn.execute(text("""
                    CREATE INDEX idx_menus_dia_carta_activo ON menus_dia_carta(activo)
                """))
                
                conn.commit()
                logger.info("✅ Tabla menus_dia_carta creada")
            else:
                logger.info("ℹ️ Tabla menus_dia_carta ya existe")
                
        except Exception as e:
            logger.error(f"Error creando menus_dia_carta: {e}")
            raise

def create_menu_opciones_table(engine):
    """Crear tabla menu_opciones"""
    logger.info("🔄 Creando tabla menu_opciones...")
    
    with engine.connect() as conn:
        try:
            # Verificar si la tabla ya existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'menu_opciones'
                )
            """))
            
            table_exists = result.scalar()
            
            if not table_exists:
                conn.execute(text("""
                    CREATE TABLE menu_opciones (
                        id SERIAL PRIMARY KEY,
                        menu_id INTEGER NOT NULL REFERENCES menus_dia_carta(menu_id) ON DELETE CASCADE,
                        producto_id INTEGER NOT NULL REFERENCES carta_restaurante(producto_id) ON DELETE CASCADE,
                        es_fijo BOOLEAN NOT NULL,
                        orden INTEGER DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        UNIQUE(menu_id, producto_id)
                    )
                """))
                
                # Crear índices
                conn.execute(text("""
                    CREATE INDEX idx_menu_opciones_menu_id ON menu_opciones(menu_id)
                """))
                
                conn.execute(text("""
                    CREATE INDEX idx_menu_opciones_producto_id ON menu_opciones(producto_id)
                """))
                
                conn.execute(text("""
                    CREATE INDEX idx_menu_opciones_es_fijo ON menu_opciones(es_fijo)
                """))
                
                conn.commit()
                logger.info("✅ Tabla menu_opciones creada")
            else:
                logger.info("ℹ️ Tabla menu_opciones ya existe")
                
        except Exception as e:
            logger.error(f"Error creando menu_opciones: {e}")
            raise

def update_order_items_table(engine):
    """Actualizar tabla order_items para soportar carta_restaurante"""
    logger.info("🔄 Actualizando tabla order_items...")
    
    with engine.connect() as conn:
        try:
            # Agregar columna para carta_restaurante
            conn.execute(text("""
                ALTER TABLE order_items 
                ADD COLUMN IF NOT EXISTS carta_producto_id INTEGER REFERENCES carta_restaurante(producto_id)
            """))
            
            # Agregar columna para menu_id
            conn.execute(text("""
                ALTER TABLE order_items 
                ADD COLUMN IF NOT EXISTS menu_id INTEGER REFERENCES menus_dia_carta(menu_id)
            """))
            
            # Agregar columna para observaciones específicas
            conn.execute(text("""
                ALTER TABLE order_items 
                ADD COLUMN IF NOT EXISTS observaciones_menu TEXT
            """))
            
            conn.commit()
            logger.info("✅ Tabla order_items actualizada")
            
        except Exception as e:
            logger.error(f"Error actualizando order_items: {e}")
            raise

def migrate_existing_products(engine):
    """Migrar productos existentes a carta_restaurante"""
    logger.info("🔄 Migrando productos existentes...")
    
    with engine.connect() as conn:
        try:
            # Verificar si ya hay datos en carta_restaurante
            result = conn.execute(text("SELECT COUNT(*) FROM carta_restaurante"))
            count = result.scalar()
            
            if count > 0:
                logger.info("ℹ️ Ya hay productos en carta_restaurante, saltando migración")
                return
            
            # Migrar productos de venta a carta_restaurante
            conn.execute(text("""
                INSERT INTO carta_restaurante (nombre, descripcion, precio_base, tipo, activo, categoria)
                SELECT 
                    name,
                    description,
                    COALESCE(precio_base, 0),
                    CASE 
                        WHEN es_fijo = true THEN 'Fijo'
                        ELSE 'Variable'
                    END,
                    COALESCE(activo, true),
                    CASE 
                        WHEN category = 'ENTRADA' THEN 'Entrada'
                        WHEN category = 'PLATO_PRINCIPAL' THEN 'Plato Principal'
                        WHEN category = 'POSTRE' THEN 'Postre'
                        WHEN category = 'BEBIDA' THEN 'Bebida'
                        WHEN category = 'ALCOHOL' THEN 'Bebida'
                        ELSE 'Otro'
                    END
                FROM products 
                WHERE product_type = 'sales' OR product_type IS NULL
            """))
            
            conn.commit()
            logger.info("✅ Productos migrados a carta_restaurante")
            
        except Exception as e:
            logger.error(f"Error migrando productos: {e}")
            raise

def create_sample_data(engine):
    """Crear datos de ejemplo"""
    logger.info("🔄 Creando datos de ejemplo...")
    
    with engine.connect() as conn:
        try:
            # Verificar si ya hay datos
            result = conn.execute(text("SELECT COUNT(*) FROM carta_restaurante"))
            count = result.scalar()
            
            if count > 0:
                logger.info("ℹ️ Ya hay datos en carta_restaurante, saltando creación de ejemplos")
                return
            
            # Insertar platos fijos
            platos_fijos = [
                ("Chuleta de Cerdo", "Chuleta de cerdo a la plancha con especias", 15.00, "Fijo", "Plato Principal"),
                ("Costillas BBQ", "Costillas de cerdo con salsa BBQ", 18.00, "Fijo", "Plato Principal"),
                ("Frijolada", "Frijoles rojos con carne y verduras", 12.00, "Fijo", "Plato Principal"),
                ("Arroz Blanco", "Arroz blanco cocido", 3.00, "Fijo", "Acompañamiento"),
                ("Ensalada Verde", "Ensalada de lechuga, tomate y cebolla", 5.00, "Fijo", "Acompañamiento")
            ]
            
            for nombre, descripcion, precio, tipo, categoria in platos_fijos:
                conn.execute(text("""
                    INSERT INTO carta_restaurante (nombre, descripcion, precio_base, tipo, activo, categoria)
                    VALUES (:nombre, :descripcion, :precio, :tipo, true, :categoria)
                """), {
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "precio": precio,
                    "tipo": tipo,
                    "categoria": categoria
                })
            
            # Insertar platos variables
            platos_variables = [
                ("Cerdo en Maracuyá", "Cerdo cocido en salsa de maracuyá", 16.00, "Variable", "Plato Principal"),
                ("Papas Criollas", "Papas criollas fritas", 4.00, "Variable", "Acompañamiento"),
                ("Verduras Salteadas", "Verduras mixtas salteadas", 6.00, "Variable", "Acompañamiento"),
                ("Jugo de Naranja", "Jugo natural de naranja", 4.00, "Variable", "Bebida"),
                ("Limonada", "Limonada natural", 3.00, "Variable", "Bebida")
            ]
            
            for nombre, descripcion, precio, tipo, categoria in platos_variables:
                conn.execute(text("""
                    INSERT INTO carta_restaurante (nombre, descripcion, precio_base, tipo, activo, categoria)
                    VALUES (:nombre, :descripcion, :precio, :tipo, true, :categoria)
                """), {
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "precio": precio,
                    "tipo": tipo,
                    "categoria": categoria
                })
            
            conn.commit()
            logger.info("✅ Datos de ejemplo creados")
            
        except Exception as e:
            logger.error(f"Error creando datos de ejemplo: {e}")
            raise

def verify_migration(engine):
    """Verificar que la migración se completó correctamente"""
    logger.info("🔄 Verificando migración...")
    
    with engine.connect() as conn:
        try:
            # Verificar tabla carta_restaurante
            result = conn.execute(text("SELECT COUNT(*) FROM carta_restaurante"))
            carta_count = result.scalar()
            logger.info(f"✅ Productos en carta_restaurante: {carta_count}")
            
            # Verificar tabla menus_dia_carta
            result = conn.execute(text("SELECT COUNT(*) FROM menus_dia_carta"))
            menus_count = result.scalar()
            logger.info(f"✅ Menús en menus_dia_carta: {menus_count}")
            
            # Verificar tabla menu_opciones
            result = conn.execute(text("SELECT COUNT(*) FROM menu_opciones"))
            opciones_count = result.scalar()
            logger.info(f"✅ Opciones en menu_opciones: {opciones_count}")
            
            # Mostrar algunos productos
            result = conn.execute(text("""
                SELECT nombre, tipo, categoria, precio_base 
                FROM carta_restaurante 
                ORDER BY tipo, categoria 
                LIMIT 10
            """))
            
            logger.info("📋 Productos en carta_restaurante:")
            for row in result:
                logger.info(f"  - {row[0]} ({row[1]}) - {row[2]} - ${row[3]}")
            
            logger.info("🎉 Migración verificada exitosamente!")
            
        except Exception as e:
            logger.error(f"Error verificando migración: {e}")
            raise

def main():
    """Función principal"""
    try:
        logger.info("🚀 Iniciando migración corregida a Carta Restaurante...")
        
        engine = create_engine_connection()
        
        # Crear/corregir tablas
        create_carta_restaurante_table(engine)
        create_menus_dia_carta_table(engine)
        create_menu_opciones_table(engine)
        update_order_items_table(engine)
        
        # Migrar datos
        migrate_existing_products(engine)
        create_sample_data(engine)
        
        # Verificar
        verify_migration(engine)
        
        logger.info("✅ Migración completada exitosamente!")
        
    except Exception as e:
        logger.error(f"❌ Error en migración: {e}")
        raise

if __name__ == "__main__":
    main()
