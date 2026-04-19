#!/usr/bin/env python3
"""
Script para crear las tablas de menús si no existen
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def create_menu_tables():
    """Crear las tablas de menús si no existen"""
    print("🔧 Creando tablas de menús...")
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Crear tabla platos
        print("\n📋 Creando tabla 'platos'...")
        try:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS platos (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    precio DECIMAL(10,2) NOT NULL,
                    tipo VARCHAR(20) DEFAULT 'Variable',
                    categoria VARCHAR(50) DEFAULT 'Plato Principal',
                    activo BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Tabla 'platos' creada/verificada")
        except Exception as e:
            print(f"❌ Error creando tabla 'platos': {e}")
        
        # Crear tabla menus
        print("\n📅 Creando tabla 'menus'...")
        try:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS menus (
                    id SERIAL PRIMARY KEY,
                    fecha DATE NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    activo BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Tabla 'menus' creada/verificada")
        except Exception as e:
            print(f"❌ Error creando tabla 'menus': {e}")
        
        # Crear tabla menu_platos
        print("\n🔗 Creando tabla 'menu_platos'...")
        try:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS menu_platos (
                    id SERIAL PRIMARY KEY,
                    menu_id INTEGER NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
                    plato_id INTEGER NOT NULL REFERENCES platos(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(menu_id, plato_id)
                )
            """))
            print("✅ Tabla 'menu_platos' creada/verificada")
        except Exception as e:
            print(f"❌ Error creando tabla 'menu_platos': {e}")
        
        # Insertar datos de ejemplo
        print("\n🍽️ Insertando datos de ejemplo...")
        try:
            # Verificar si ya hay datos
            result = session.execute(text("SELECT COUNT(*) FROM platos"))
            count = result.fetchone()[0]
            
            if count == 0:
                # Insertar platos de ejemplo
                platos_ejemplo = [
                    ("Sopa de Pollo", "Sopa tradicional con pollo y verduras", 12000.0, "Fijo", "Entrada"),
                    ("Arroz con Pollo", "Arroz con pollo, verduras y especias", 15000.0, "Variable", "Plato Principal"),
                    ("Ensalada César", "Ensalada fresca con aderezo césar", 8000.0, "Variable", "Entrada"),
                    ("Pollo a la Plancha", "Pechuga de pollo a la plancha con especias", 18000.0, "Variable", "Plato Principal"),
                    ("Jugo de Naranja", "Jugo natural de naranja", 5000.0, "Fijo", "Bebida"),
                    ("Postre del Día", "Postre especial del chef", 6000.0, "Variable", "Postre")
                ]
                
                for plato in platos_ejemplo:
                    session.execute(text("""
                        INSERT INTO platos (nombre, descripcion, precio, tipo, categoria)
                        VALUES (:nombre, :descripcion, :precio, :tipo, :categoria)
                    """), {
                        "nombre": plato[0],
                        "descripcion": plato[1],
                        "precio": plato[2],
                        "tipo": plato[3],
                        "categoria": plato[4]
                    })
                
                print(f"✅ {len(platos_ejemplo)} platos de ejemplo insertados")
            else:
                print(f"✅ Ya existen {count} platos en la base de datos")
        
        except Exception as e:
            print(f"❌ Error insertando datos de ejemplo: {e}")
        
        # Crear menú de ejemplo para hoy
        print("\n📅 Creando menú de ejemplo para hoy...")
        try:
            from datetime import date
            today = date.today()
            
            # Verificar si ya hay menú para hoy
            result = session.execute(text("SELECT COUNT(*) FROM menus WHERE fecha = :fecha"), {"fecha": today})
            count = result.fetchone()[0]
            
            if count == 0:
                # Crear menú para hoy
                result = session.execute(text("""
                    INSERT INTO menus (fecha, nombre, descripcion)
                    VALUES (:fecha, :nombre, :descripcion)
                    RETURNING id
                """), {
                    "fecha": today,
                    "nombre": f"Menú del {today.strftime('%d/%m/%Y')}",
                    "descripcion": "Menú especial del día"
                })
                
                menu_id = result.fetchone()[0]
                
                # Agregar algunos platos al menú
                platos_para_menu = [1, 2, 3, 4, 5, 6]  # IDs de los platos de ejemplo
                for plato_id in platos_para_menu:
                    session.execute(text("""
                        INSERT INTO menu_platos (menu_id, plato_id)
                        VALUES (:menu_id, :plato_id)
                    """), {
                        "menu_id": menu_id,
                        "plato_id": plato_id
                    })
                
                print(f"✅ Menú de ejemplo creado para hoy (ID: {menu_id})")
            else:
                print("✅ Ya existe un menú para hoy")
        
        except Exception as e:
            print(f"❌ Error creando menú de ejemplo: {e}")
        
        session.commit()
        session.close()
        
        print("\n🎉 Tablas de menús creadas exitosamente!")
        print("\n📊 Resumen:")
        print("  - ✅ Tabla 'platos' creada/verificada")
        print("  - ✅ Tabla 'menus' creada/verificada")
        print("  - ✅ Tabla 'menu_platos' creada/verificada")
        print("  - ✅ Datos de ejemplo insertados")
        print("  - ✅ Menú de ejemplo creado para hoy")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_menu_tables()
