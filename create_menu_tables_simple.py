#!/usr/bin/env python3
"""
Script simple para crear las tablas del sistema de menús
"""
import psycopg2
from psycopg2 import sql
import os

def create_menu_tables():
    """Crear las tablas del sistema de menús"""
    print("🔄 Creando tablas del sistema de menús...")
    
    # Configuración de la base de datos
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'restaurantepos',
        'user': 'postgres',
        'password': 'admin123'
    }
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Crear tabla de platos
        print("📋 Creando tabla 'platos'...")
        cursor.execute("""
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
        """)
        
        # Crear tabla de menús
        print("📅 Creando tabla 'menus'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menus (
                id SERIAL PRIMARY KEY,
                fecha DATE NOT NULL UNIQUE,
                activo BOOLEAN DEFAULT TRUE,
                nombre VARCHAR(100),
                descripcion TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE
            );
        """)
        
        # Crear tabla intermedia menu_platos
        print("🔗 Creando tabla intermedia 'menu_platos'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_platos (
                menu_id INTEGER NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
                plato_id INTEGER NOT NULL REFERENCES platos(id) ON DELETE CASCADE,
                PRIMARY KEY (menu_id, plato_id)
            );
        """)
        
        # Crear índices
        print("📊 Creando índices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_menus_fecha ON menus(fecha);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_platos_tipo ON platos(tipo);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_platos_categoria ON platos(categoria);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_platos_activo ON platos(activo);")
        
        conn.commit()
        print("✅ Tablas creadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def populate_sample_data():
    """Poblar con datos de ejemplo"""
    print("🔄 Poblando con datos de ejemplo...")
    
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'restaurantepos',
        'user': 'postgres',
        'password': 'admin123'
    }
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM platos")
        result = cursor.fetchone()
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
            cursor.execute("""
                INSERT INTO platos (nombre, descripcion, precio, tipo, categoria, activo)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            """, plato)
        
        print(f"✅ Insertados {len(platos_ejemplo)} platos de ejemplo")
        
        # Crear menú de ejemplo para hoy
        from datetime import date
        today = date.today()
        
        # Verificar si ya existe un menú para hoy
        cursor.execute("SELECT COUNT(*) FROM menus WHERE fecha = %s", (today,))
        result = cursor.fetchone()
        if result[0] == 0:
            # Crear menú de ejemplo
            cursor.execute("""
                INSERT INTO menus (fecha, activo, nombre, descripcion)
                VALUES (%s, TRUE, %s, %s)
            """, (today, f"Menú del Día - {today.strftime('%d/%m/%Y')}", "Menú de ejemplo con platos fijos y variables"))
            
            # Obtener ID del menú creado
            cursor.execute("SELECT id FROM menus WHERE fecha = %s", (today,))
            result = cursor.fetchone()
            menu_id = result[0]
            
            # Asociar platos al menú (todos los platos de ejemplo)
            plato_ids = [i+1 for i in range(len(platos_ejemplo))]  # IDs 1, 2, 3, 4, 5, 6, 7, 8
            
            for plato_id in plato_ids:
                cursor.execute("""
                    INSERT INTO menu_platos (menu_id, plato_id)
                    VALUES (%s, %s)
                """, (menu_id, plato_id))
            
            print(f"✅ Creado menú de ejemplo para {today}")
        
        conn.commit()
        print("🎉 Datos de ejemplo insertados exitosamente")
        
    except Exception as e:
        print(f"❌ Error poblando datos: {e}")
        conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


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
