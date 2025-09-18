#!/usr/bin/env python3
"""
Script para crear las tablas del sistema de menús usando SQLAlchemy
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database import get_db
from app.models.menu_unified import Menu, Plato, menu_platos
from datetime import date

def create_menu_tables():
    """Crear las tablas del sistema de menús usando SQLAlchemy"""
    print("🔄 Creando tablas del sistema de menús...")
    
    try:
        # Obtener la sesión de la base de datos
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
            ("Arroz", "Arroz blanco", "0", "Fijo", "Acompañamiento"),
            ("Ensalada", "Ensalada mixta", "0", "Fijo", "Acompañamiento"),
            ("Bebida", "Bebida del día", "0", "Fijo", "Bebida"),
            
            # Platos variables
            ("Pollo a la plancha", "Pollo a la plancha con especias", "12000", "Variable", "Plato Principal"),
            ("Carne de res", "Carne de res a la parrilla", "15000", "Variable", "Plato Principal"),
            ("Pescado frito", "Pescado fresco frito", "14000", "Variable", "Plato Principal"),
            ("Sopa de pollo", "Sopa de pollo casera", "8000", "Variable", "Entrada"),
            ("Crema de verduras", "Crema de verduras frescas", "7000", "Variable", "Entrada"),
        ]
        
        for plato in platos_ejemplo:
            db.execute(text("""
                INSERT INTO platos (nombre, descripcion, precio, tipo, categoria, activo)
                VALUES (:nombre, :descripcion, :precio, :tipo, :categoria, TRUE)
            """), {
                "nombre": plato[0],
                "descripcion": plato[1],
                "precio": plato[2],
                "tipo": plato[3],
                "categoria": plato[4]
            })
        
        print(f"✅ Insertados {len(platos_ejemplo)} platos de ejemplo")
        
        # Crear menú de ejemplo para hoy
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


def main():
    """Función principal"""
    print("🚀 Iniciando creación del sistema de menús...")
    
    create_menu_tables()
    populate_sample_data()
    
    print("\n🎉 Sistema de menús creado exitosamente!")
    print(f"\n🌐 Puedes probar el sistema en:")
    print(f"  - API: http://127.0.0.1:8000/api/v1/public/menus/stats/")
    print(f"  - Interfaz: http://127.0.0.1:8000/admin/menus")


if __name__ == "__main__":
    main()
