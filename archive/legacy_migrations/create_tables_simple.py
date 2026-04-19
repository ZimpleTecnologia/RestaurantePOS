#!/usr/bin/env python3
"""
Script simple para crear las tablas del sistema de menús usando la configuración del proyecto
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_restaurant_menu_tables():
    """Crear las tablas del sistema de menús del restaurante"""
    print("🔧 Creando tablas del sistema de menús del restaurante...")
    
    try:
        # Usar la configuración del proyecto
        from app.config import settings
        
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ Conectado a la base de datos")
        
        # 1. Crear tabla categorias_menu
        print("\n📋 Creando tabla 'categorias_menu'...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS categorias_menu (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL UNIQUE,
                descripcion TEXT,
                orden INTEGER DEFAULT 0,
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Tabla 'categorias_menu' creada/verificada")
        
        # 2. Crear tabla platos_restaurante
        print("\n🍽️ Creando tabla 'platos_restaurante'...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS platos_restaurante (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                precio DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Menu_Dia', 'Plato_Fijo', 'Acompanamiento_Fijo')),
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Tabla 'platos_restaurante' creada/verificada")
        
        # 3. Crear tabla menu_dia
        print("\n📅 Creando tabla 'menu_dia'...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS menu_dia (
                id SERIAL PRIMARY KEY,
                fecha DATE NOT NULL UNIQUE,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                activo BOOLEAN DEFAULT TRUE,
                publicado BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Tabla 'menu_dia' creada/verificada")
        
        # 4. Crear tabla menu_categoria_platos
        print("\n🔗 Creando tabla 'menu_categoria_platos'...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS menu_categoria_platos (
                id SERIAL PRIMARY KEY,
                menu_dia_id INTEGER NOT NULL REFERENCES menu_dia(id) ON DELETE CASCADE,
                categoria_id INTEGER NOT NULL REFERENCES categorias_menu(id) ON DELETE CASCADE,
                plato_id INTEGER NOT NULL REFERENCES platos_restaurante(id) ON DELETE CASCADE,
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(menu_dia_id, categoria_id, plato_id)
            )
        """))
        print("✅ Tabla 'menu_categoria_platos' creada/verificada")
        
        # 5. Crear tabla acompanamientos_fijos
        print("\n🥗 Creando tabla 'acompanamientos_fijos'...")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS acompanamientos_fijos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                activo BOOLEAN DEFAULT TRUE,
                orden INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Tabla 'acompanamientos_fijos' creada/verificada")
        
        # 6. Insertar categorías por defecto
        print("\n📋 Insertando categorías por defecto...")
        categorias_default = [
            ("Principio", "Platos de entrada o principio", 1),
            ("Proteína", "Platos principales con proteína", 2)
        ]
        
        for nombre, descripcion, orden in categorias_default:
            session.execute(text("""
                INSERT INTO categorias_menu (nombre, descripcion, orden)
                VALUES (:nombre, :descripcion, :orden)
                ON CONFLICT (nombre) DO NOTHING
            """), {"nombre": nombre, "descripcion": descripcion, "orden": orden})
            print(f"✅ Categoría '{nombre}' insertada/verificada")
        
        # 7. Insertar acompañamientos fijos por defecto
        print("\n🥗 Insertando acompañamientos fijos por defecto...")
        acompanamientos_default = [
            ("Plátano maduro", "Plátano maduro frito", 1),
            ("Arroz", "Arroz blanco", 2),
            ("Ensalada", "Ensalada fresca", 3),
            ("Sopa", "Sopa del día", 4),
            ("Bebida", "Bebida del día", 5)
        ]
        
        for nombre, descripcion, orden in acompanamientos_default:
            session.execute(text("""
                INSERT INTO acompanamientos_fijos (nombre, descripcion, orden)
                VALUES (:nombre, :descripcion, :orden)
                ON CONFLICT DO NOTHING
            """), {"nombre": nombre, "descripcion": descripcion, "orden": orden})
            print(f"✅ Acompañamiento '{nombre}' insertado/verificado")
        
        # 8. Insertar platos de ejemplo
        print("\n🍽️ Insertando platos de ejemplo...")
        platos_ejemplo = [
            # Platos para menú del día
            ("Verduras a la crema", "Verduras frescas en crema", 0.0, "Menu_Dia"),
            ("Frijoles", "Frijoles tradicionales", 0.0, "Menu_Dia"),
            ("Pechuga a la plancha", "Pechuga de pollo a la plancha", 0.0, "Menu_Dia"),
            ("Carne de cerdo", "Carne de cerdo asada", 0.0, "Menu_Dia"),
            ("Hígado encebollado", "Hígado con cebolla", 0.0, "Menu_Dia"),
            
            # Platos fijos
            ("Frijolada", "Frijolada tradicional", 15000.0, "Plato_Fijo"),
            ("Chicharrón al barril", "Chicharrón al barril", 18000.0, "Plato_Fijo")
        ]
        
        for nombre, descripcion, precio, tipo in platos_ejemplo:
            session.execute(text("""
                INSERT INTO platos_restaurante (nombre, descripcion, precio, tipo)
                VALUES (:nombre, :descripcion, :precio, :tipo)
                ON CONFLICT DO NOTHING
            """), {"nombre": nombre, "descripcion": descripcion, "precio": precio, "tipo": tipo})
            print(f"✅ Plato '{nombre}' insertado/verificado")
        
        # 9. Crear menú de ejemplo para hoy
        print("\n📅 Creando menú de ejemplo para hoy...")
        from datetime import date
        today = date.today()
        
        # Verificar si ya hay menú para hoy
        result = session.execute(text("SELECT COUNT(*) FROM menu_dia WHERE fecha = :fecha"), {"fecha": today})
        count = result.fetchone()[0]
        
        if count == 0:
            # Crear menú para hoy
            result = session.execute(text("""
                INSERT INTO menu_dia (fecha, nombre, descripcion, publicado)
                VALUES (:fecha, :nombre, :descripcion, :publicado)
                RETURNING id
            """), {
                "fecha": today,
                "nombre": f"Almuerzo del {today.strftime('%d/%m/%Y')}",
                "descripcion": "Menú especial del día",
                "publicado": True
            })
            
            menu_id = result.fetchone()[0]
            print(f"✅ Menú de hoy creado (ID: {menu_id})")
            
            # Agregar platos al menú por categoría
            # Obtener IDs de categorías
            result = session.execute(text("SELECT id, nombre FROM categorias_menu"))
            categorias = {nombre: id for id, nombre in result.fetchall()}
            
            # Obtener IDs de platos
            result = session.execute(text("SELECT id, nombre FROM platos_restaurante WHERE tipo = 'Menu_Dia'"))
            platos = {nombre: id for id, nombre in result.fetchall()}
            
            # Agregar platos por categoría
            menu_categorias = {
                "Principio": ["Verduras a la crema", "Frijoles"],
                "Proteína": ["Pechuga a la plancha", "Carne de cerdo", "Hígado encebollado"]
            }
            
            for categoria_nombre, platos_nombres in menu_categorias.items():
                categoria_id = categorias.get(categoria_nombre)
                if categoria_id:
                    for plato_nombre in platos_nombres:
                        plato_id = platos.get(plato_nombre)
                        if plato_id:
                            session.execute(text("""
                                INSERT INTO menu_categoria_platos (menu_dia_id, categoria_id, plato_id)
                                VALUES (:menu_dia_id, :categoria_id, :plato_id)
                                ON CONFLICT DO NOTHING
                            """), {"menu_dia_id": menu_id, "categoria_id": categoria_id, "plato_id": plato_id})
                            print(f"✅ Agregado '{plato_nombre}' a categoría '{categoria_nombre}'")
        else:
            print("✅ Ya existe un menú para hoy")
        
        # Confirmar cambios
        session.commit()
        print("\n🎉 Tablas del sistema de menús creadas exitosamente!")
        
        # Mostrar resumen
        print("\n📊 Resumen de tablas creadas:")
        print("  - ✅ categorias_menu: Categorías de platos")
        print("  - ✅ platos_restaurante: Platos del restaurante")
        print("  - ✅ menu_dia: Menús del día")
        print("  - ✅ menu_categoria_platos: Relación menú-categoría-plato")
        print("  - ✅ acompanamientos_fijos: Acompañamientos que siempre se incluyen")
        
        print("\n🍽️ Datos de ejemplo insertados:")
        print("  - ✅ Categorías: Principio, Proteína")
        print("  - ✅ Acompañamientos fijos: Plátano, Arroz, Ensalada, Sopa, Bebida")
        print("  - ✅ Platos de ejemplo: Verduras, Frijoles, Pechuga, Carne, Hígado")
        print("  - ✅ Platos fijos: Frijolada, Chicharrón al barril")
        print("  - ✅ Menú del día: Creado y publicado para hoy")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_restaurant_menu_tables()


