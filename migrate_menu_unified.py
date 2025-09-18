#!/usr/bin/env python3
"""
Script de migración para el sistema de menús unificado
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, engine
from app.models.menu_unified import Menu, Plato, menu_platos
from sqlalchemy import text

def create_menu_tables():
    """Crear las tablas del sistema de menús unificado"""
    print("🔄 Creando tablas del sistema de menús unificado...")
    
    try:
        db = next(get_db())
        
        # Crear tabla de platos
        print("📋 Creando tabla 'platos'...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS platos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                precio VARCHAR(20) NOT NULL,
                tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Fijo', 'Variable')),
                categoria VARCHAR(50),
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            );
        """))
        
        # Crear tabla de menús
        print("📅 Creando tabla 'menus'...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS menus (
                id SERIAL PRIMARY KEY,
                fecha DATE NOT NULL UNIQUE,
                activo BOOLEAN DEFAULT TRUE,
                nombre VARCHAR(100),
                descripcion TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            );
        """))
        
        # Crear tabla intermedia menu_platos
        print("🔗 Creando tabla intermedia 'menu_platos'...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS menu_platos (
                menu_id INTEGER NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
                plato_id INTEGER NOT NULL REFERENCES platos(id) ON DELETE CASCADE,
                PRIMARY KEY (menu_id, plato_id)
            );
        """))
        
        # Crear índices
        print("📊 Creando índices...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_menus_fecha ON menus(fecha);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_platos_tipo ON platos(tipo);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_platos_categoria ON platos(categoria);"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_platos_activo ON platos(activo);"))
        
        db.commit()
        print("✅ Tablas creadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def populate_sample_data():
    """Poblar con datos de ejemplo"""
    print("🔄 Poblando con datos de ejemplo...")
    
    try:
        db = next(get_db())
        
        # Verificar si ya hay datos
        result = db.execute(text("SELECT COUNT(*) FROM platos")).fetchone()
        if result[0] > 0:
            print("ℹ️ Ya hay datos en la tabla platos, saltando...")
            return
        
        # Insertar platos de ejemplo
        platos_ejemplo = [
            # Platos fijos
            {"nombre": "Arroz", "descripcion": "Arroz blanco", "precio": "0", "tipo": "Fijo", "categoria": "Acompañamiento"},
            {"nombre": "Ensalada", "descripcion": "Ensalada mixta", "precio": "0", "tipo": "Fijo", "categoria": "Acompañamiento"},
            {"nombre": "Bebida", "descripcion": "Bebida del día", "precio": "0", "tipo": "Fijo", "categoria": "Bebida"},
            
            # Platos variables
            {"nombre": "Pollo a la plancha", "descripcion": "Pollo a la plancha con especias", "precio": "12000", "tipo": "Variable", "categoria": "Plato Principal"},
            {"nombre": "Carne de res", "descripcion": "Carne de res a la parrilla", "precio": "15000", "tipo": "Variable", "categoria": "Plato Principal"},
            {"nombre": "Pescado frito", "descripcion": "Pescado fresco frito", "precio": "14000", "tipo": "Variable", "categoria": "Plato Principal"},
            {"nombre": "Sopa de pollo", "descripcion": "Sopa de pollo casera", "precio": "8000", "tipo": "Variable", "categoria": "Entrada"},
            {"nombre": "Crema de verduras", "descripcion": "Crema de verduras frescas", "precio": "7000", "tipo": "Variable", "categoria": "Entrada"},
        ]
        
        for plato in platos_ejemplo:
            db.execute(text("""
                INSERT INTO platos (nombre, descripcion, precio, tipo, categoria, activo)
                VALUES (:nombre, :descripcion, :precio, :tipo, :categoria, TRUE)
            """), plato)
        
        print(f"✅ Insertados {len(platos_ejemplo)} platos de ejemplo")
        
        # Crear menú de ejemplo para hoy
        from datetime import date
        today = date.today()
        
        # Verificar si ya existe un menú para hoy
        result = db.execute(text("SELECT COUNT(*) FROM menus WHERE fecha = :fecha"), {"fecha": today}).fetchone()
        if result[0] == 0:
            # Crear menú de ejemplo
            db.execute(text("""
                INSERT INTO menus (fecha, activo, nombre, descripcion)
                VALUES (:fecha, TRUE, :nombre, :descripcion)
            """), {
                "fecha": today,
                "nombre": f"Menú del Día - {today.strftime('%d/%m/%Y')}",
                "descripcion": "Menú de ejemplo con platos fijos y variables"
            })
            
            # Obtener ID del menú creado
            result = db.execute(text("SELECT id FROM menus WHERE fecha = :fecha"), {"fecha": today}).fetchone()
            menu_id = result[0]
            
            # Asociar platos al menú (todos los platos de ejemplo)
            plato_ids = [i+1 for i in range(len(platos_ejemplo))]  # IDs 1, 2, 3, 4, 5, 6, 7, 8
            
            for plato_id in plato_ids:
                db.execute(text("""
                    INSERT INTO menu_platos (menu_id, plato_id)
                    VALUES (:menu_id, :plato_id)
                """), {"menu_id": menu_id, "plato_id": plato_id})
            
            print(f"✅ Creado menú de ejemplo para {today}")
        
        db.commit()
        print("🎉 Datos de ejemplo insertados exitosamente")
        
    except Exception as e:
        print(f"❌ Error poblando datos: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def verify_migration():
    """Verificar que la migración fue exitosa"""
    print("🔍 Verificando migración...")
    
    try:
        db = next(get_db())
        
        # Verificar tablas
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('menus', 'platos', 'menu_platos')
            ORDER BY table_name
        """)).fetchall()
        
        print("📋 Tablas creadas:")
        for table in result:
            print(f"  ✅ {table[0]}")
        
        # Verificar datos
        platos_count = db.execute(text("SELECT COUNT(*) FROM platos")).fetchone()[0]
        menus_count = db.execute(text("SELECT COUNT(*) FROM menus")).fetchone()[0]
        
        print(f"\n📊 Datos:")
        print(f"  - Platos: {platos_count}")
        print(f"  - Menús: {menus_count}")
        
        if platos_count > 0 and menus_count > 0:
            print("\n🎉 Migración exitosa!")
            print(f"\n🌐 Puedes probar el sistema en:")
            print(f"  - API: http://127.0.0.1:8000/api/v1/menus/")
            print(f"  - Interfaz: http://127.0.0.1:8000/menu-management")
        else:
            print("\n⚠️ Migración completada pero sin datos de ejemplo")
        
    except Exception as e:
        print(f"❌ Error verificando migración: {e}")
    finally:
        db.close()


def main():
    """Función principal"""
    print("🚀 Iniciando migración del sistema de menús unificado...")
    
    create_menu_tables()
    populate_sample_data()
    verify_migration()


if __name__ == "__main__":
    main()
