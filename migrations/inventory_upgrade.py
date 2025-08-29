#!/usr/bin/env python3
"""
Script de migración para actualizar el módulo de inventario a la versión profesionalizada
"""
import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Configurar variables de entorno para Docker
os.environ["DATABASE_URL"] = "postgresql://sistema_pos_user:sistema_pos_password@postgres:5432/sistema_pos"
os.environ["SECRET_KEY"] = "tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DEBUG"] = "True"

# Agregar path de la aplicación
sys.path.insert(0, '/app')

from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric, Enum, Date, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL

def create_inventory_tables():
    """Crear las nuevas tablas de inventario"""
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()
    
    print("🔧 Creando nuevas tablas de inventario...")
    
    # Tabla de ubicaciones de inventario
    inventory_locations = Table(
        'inventory_locations', metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String(100), nullable=False, unique=True),
        Column('description', Text, nullable=True),
        Column('is_active', Boolean, default=True),
        Column('is_default', Boolean, default=False),
        Column('created_at', DateTime(timezone=True), server_default=text('now()')),
        Column('updated_at', DateTime(timezone=True), onupdate=text('now()'))
    )
    
    # Tabla de lotes de inventario
    inventory_lots = Table(
        'inventory_lots', metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('product_id', Integer, ForeignKey('products.id'), nullable=False),
        Column('location_id', Integer, ForeignKey('inventory_locations.id'), nullable=False),
        Column('lot_number', String(50), nullable=False),
        Column('batch_number', String(50), nullable=True),
        Column('supplier_lot', String(50), nullable=True),
        Column('quantity', Integer, nullable=False, default=0),
        Column('reserved_quantity', Integer, nullable=False, default=0),
        Column('available_quantity', Integer, nullable=False, default=0),
        Column('unit_cost', Numeric(10, 2), nullable=True),
        Column('total_cost', Numeric(10, 2), nullable=True),
        Column('manufacturing_date', Date, nullable=True),
        Column('expiration_date', Date, nullable=True),
        Column('best_before_date', Date, nullable=True),
        Column('supplier_id', Integer, ForeignKey('suppliers.id'), nullable=True),
        Column('purchase_order', String(50), nullable=True),
        Column('invoice_number', String(50), nullable=True),
        Column('is_active', Boolean, default=True),
        Column('created_at', DateTime(timezone=True), server_default=text('now()')),
        Column('updated_at', DateTime(timezone=True), onupdate=text('now()'))
    )
    
    # Tabla de alertas de inventario
    inventory_alerts = Table(
        'inventory_alerts', metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('product_id', Integer, ForeignKey('products.id'), nullable=False),
        Column('lot_id', Integer, ForeignKey('inventory_lots.id'), nullable=True),
        Column('alert_type', String(50), nullable=False),
        Column('alert_level', String(20), nullable=False),
        Column('message', Text, nullable=False),
        Column('is_active', Boolean, default=True),
        Column('is_acknowledged', Boolean, default=False),
        Column('acknowledged_by', Integer, ForeignKey('users.id'), nullable=True),
        Column('acknowledged_at', DateTime(timezone=True), nullable=True),
        Column('created_at', DateTime(timezone=True), server_default=text('now()'))
    )
    
    # Tabla de conteos físicos
    inventory_counts = Table(
        'inventory_counts', metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('count_number', String(50), nullable=False, unique=True),
        Column('count_date', Date, nullable=False),
        Column('location_id', Integer, ForeignKey('inventory_locations.id'), nullable=True),
        Column('status', String(20), nullable=False, default='draft'),
        Column('notes', Text, nullable=True),
        Column('created_by', Integer, ForeignKey('users.id'), nullable=False),
        Column('created_at', DateTime(timezone=True), server_default=text('now()')),
        Column('completed_at', DateTime(timezone=True), nullable=True)
    )
    
    # Tabla de items de conteo físico
    inventory_count_items = Table(
        'inventory_count_items', metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('count_id', Integer, ForeignKey('inventory_counts.id'), nullable=False),
        Column('product_id', Integer, ForeignKey('products.id'), nullable=False),
        Column('lot_id', Integer, ForeignKey('inventory_lots.id'), nullable=True),
        Column('expected_quantity', Integer, nullable=False),
        Column('actual_quantity', Integer, nullable=True),
        Column('variance', Integer, nullable=True),
        Column('variance_percentage', Float, nullable=True),
        Column('notes', Text, nullable=True)
    )
    
    # Crear las tablas
    metadata.create_all(engine)
    print("✅ Tablas de inventario creadas exitosamente")


def update_products_table():
    """Actualizar la tabla de productos con nuevas columnas"""
    engine = create_engine(DATABASE_URL)
    
    print("🔧 Actualizando tabla de productos...")
    
    # Agregar nuevas columnas a la tabla products
    with engine.connect() as conn:
        # Verificar si las columnas ya existen
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' 
            AND column_name IN ('track_lots', 'track_expiration', 'shelf_life_days', 'reorder_point', 'reorder_quantity', 'default_location_id', 'barcode', 'sku', 'weight', 'dimensions', 'unit_of_measure')
        """))
        existing_columns = [row[0] for row in result]
        
        # Columnas a agregar
        new_columns = [
            ('track_lots', 'BOOLEAN DEFAULT FALSE'),
            ('track_expiration', 'BOOLEAN DEFAULT FALSE'),
            ('shelf_life_days', 'INTEGER'),
            ('reorder_point', 'INTEGER DEFAULT 0'),
            ('reorder_quantity', 'INTEGER DEFAULT 0'),
            ('default_location_id', 'INTEGER REFERENCES inventory_locations(id)'),
            ('barcode', 'VARCHAR(100)'),
            ('sku', 'VARCHAR(100)'),
            ('weight', 'FLOAT'),
            ('dimensions', 'VARCHAR(50)'),
            ('unit_of_measure', 'VARCHAR(20) DEFAULT \'unidad\'')
        ]
        
        for column_name, column_definition in new_columns:
            if column_name not in existing_columns:
                try:
                    conn.execute(text(f"ALTER TABLE products ADD COLUMN {column_name} {column_definition}"))
                    print(f"  ✅ Columna {column_name} agregada")
                except Exception as e:
                    print(f"  ⚠️ Error agregando columna {column_name}: {e}")
            else:
                print(f"  ℹ️ Columna {column_name} ya existe")
        
        conn.commit()
    
    print("✅ Tabla de productos actualizada")


def update_inventory_movements_table():
    """Actualizar la tabla de movimientos de inventario"""
    engine = create_engine(DATABASE_URL)
    
    print("🔧 Actualizando tabla de movimientos de inventario...")
    
    with engine.connect() as conn:
        # Verificar si las columnas ya existen
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'inventory_movements' 
            AND column_name IN ('lot_id', 'location_id', 'movement_type', 'reason', 'reason_detail', 'unit_cost', 'total_cost', 'reference_type', 'reference_id', 'reference_number', 'tags', 'updated_at')
        """))
        existing_columns = [row[0] for row in result]
        
        # Columnas a agregar
        new_columns = [
            ('lot_id', 'INTEGER REFERENCES inventory_lots(id)'),
            ('location_id', 'INTEGER REFERENCES inventory_locations(id)'),
            ('movement_type', 'VARCHAR(50)'),
            ('reason', 'VARCHAR(50)'),
            ('reason_detail', 'VARCHAR(200)'),
            ('unit_cost', 'NUMERIC(10,2)'),
            ('total_cost', 'NUMERIC(10,2)'),
            ('reference_type', 'VARCHAR(50)'),
            ('reference_id', 'INTEGER'),
            ('reference_number', 'VARCHAR(50)'),
            ('tags', 'VARCHAR(200)'),
            ('updated_at', 'TIMESTAMP WITH TIME ZONE')
        ]
        
        for column_name, column_definition in new_columns:
            if column_name not in existing_columns:
                try:
                    conn.execute(text(f"ALTER TABLE inventory_movements ADD COLUMN {column_name} {column_definition}"))
                    print(f"  ✅ Columna {column_name} agregada")
                except Exception as e:
                    print(f"  ⚠️ Error agregando columna {column_name}: {e}")
            else:
                print(f"  ℹ️ Columna {column_name} ya existe")
        
        # Crear índices para optimización
        indexes = [
            ('idx_movement_product_date', 'inventory_movements(product_id, created_at)'),
            ('idx_movement_type_date', 'inventory_movements(movement_type, created_at)'),
            ('idx_movement_reference', 'inventory_movements(reference_type, reference_id)'),
            ('idx_movement_user_date', 'inventory_movements(user_id, created_at)'),
            ('idx_lot_product_location', 'inventory_lots(product_id, location_id)'),
            ('idx_lot_expiration', 'inventory_lots(expiration_date)'),
            ('idx_lot_number', 'inventory_lots(lot_number)')
        ]
        
        for index_name, index_definition in indexes:
            try:
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_definition}"))
                print(f"  ✅ Índice {index_name} creado")
            except Exception as e:
                print(f"  ⚠️ Error creando índice {index_name}: {e}")
        
        conn.commit()
    
    print("✅ Tabla de movimientos de inventario actualizada")


def create_default_location():
    """Crear ubicación por defecto"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si ya existe una ubicación por defecto
        result = db.execute(text("SELECT COUNT(*) FROM inventory_locations WHERE is_default = TRUE"))
        count = result.scalar()
        
        if count == 0:
            # Crear ubicación por defecto
            db.execute(text("""
                INSERT INTO inventory_locations (name, description, is_active, is_default, created_at)
                VALUES ('Almacén Principal', 'Ubicación principal del almacén', TRUE, TRUE, NOW())
            """))
            db.commit()
            print("✅ Ubicación por defecto creada")
        else:
            print("ℹ️ Ya existe una ubicación por defecto")
    
    except Exception as e:
        print(f"⚠️ Error creando ubicación por defecto: {e}")
        db.rollback()
    finally:
        db.close()


def migrate_existing_data():
    """Migrar datos existentes al nuevo formato"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    print("🔧 Migrando datos existentes...")
    
    try:
        # Migrar movimientos existentes al nuevo formato
        db.execute(text("""
            UPDATE inventory_movements 
            SET movement_type = CASE 
                WHEN adjustment_type = 'add' THEN 'entrada'
                WHEN adjustment_type = 'subtract' THEN 'salida'
                WHEN adjustment_type = 'set' THEN 'ajuste'
                ELSE 'ajuste'
            END,
            reason = CASE 
                WHEN adjustment_type = 'add' THEN 'ajuste_positivo'
                WHEN adjustment_type = 'subtract' THEN 'ajuste_negativo'
                WHEN adjustment_type = 'set' THEN 'ajuste_positivo'
                ELSE 'ajuste_positivo'
            END
            WHERE movement_type IS NULL
        """))
        
        # Actualizar productos con configuración por defecto
        db.execute(text("""
            UPDATE products 
            SET track_lots = FALSE,
                track_expiration = FALSE,
                reorder_point = min_stock,
                unit_of_measure = 'unidad'
            WHERE track_lots IS NULL
        """))
        
        db.commit()
        print("✅ Datos migrados exitosamente")
    
    except Exception as e:
        print(f"⚠️ Error migrando datos: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Función principal de migración"""
    print("🚀 Iniciando migración del módulo de inventario...")
    
    try:
        # 1. Crear nuevas tablas
        create_inventory_tables()
        
        # 2. Actualizar tabla de productos
        update_products_table()
        
        # 3. Actualizar tabla de movimientos
        update_inventory_movements_table()
        
        # 4. Crear ubicación por defecto
        create_default_location()
        
        # 5. Migrar datos existentes
        migrate_existing_data()
        
        print("🎉 Migración completada exitosamente!")
        print("\n📋 Resumen de cambios:")
        print("  ✅ Nuevas tablas: inventory_locations, inventory_lots, inventory_alerts, inventory_counts, inventory_count_items")
        print("  ✅ Columnas agregadas a products: track_lots, track_expiration, shelf_life_days, etc.")
        print("  ✅ Columnas agregadas a inventory_movements: lot_id, location_id, movement_type, etc.")
        print("  ✅ Índices de optimización creados")
        print("  ✅ Ubicación por defecto configurada")
        print("  ✅ Datos existentes migrados")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
