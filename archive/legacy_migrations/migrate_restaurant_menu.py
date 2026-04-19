#!/usr/bin/env python3
"""
Script de migración para el nuevo sistema de menús del restaurante
Crea las tablas necesarias para el sistema de menús con categorías
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def create_restaurant_menu_tables():
    """Crear las tablas del sistema de menús del restaurante"""
    print("🔧 Creando tablas del sistema de menús del restaurante...")
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 1. Crear tabla categorias_menu
        print("\n📋 Creando tabla 'categorias_menu'...")
        try:
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
        except Exception as e:
            print(f"❌ Error creando tabla 'categorias_menu': {e}")
        
        # 2. Crear tabla platos_restaurante
        print("\n🍽️ Creando tabla 'platos_restaurante'...")
        try:
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
        except Exception as e:
            print(f"❌ Error creando tabla 'platos_restaurante': {e}")
        
        # 3. Crear tabla menu_dia
        print("\n📅 Creando tabla 'menu_dia'...")
        try:
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
        except Exception as e:
            print(f"❌ Error creando tabla 'menu_dia': {e}")
        
        # 4. Crear tabla menu_categoria_platos
        print("\n🔗 Creando tabla 'menu_categoria_platos'...")
        try:
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
        except Exception as e:
            print(f"❌ Error creando tabla 'menu_categoria_platos': {e}")
        
        # 5. Crear tabla acompanamientos_fijos
        print("\n🥗 Creando tabla 'acompanamientos_fijos'...")
        try:
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
        except Exception as e:
            print(f"❌ Error creando tabla 'acompanamientos_fijos': {e}")
        
        # 6. Insertar categorías por defecto
        print("\n📋 Insertando categorías por defecto...")
        try:
            categorias_default = [
                ("Principio", "Platos de entrada o principio", 1),
                ("Proteína", "Platos principales con proteína", 2)
            ]
            
            for nombre, descripcion, orden in categorias_default:
                # Verificar si ya existe
                result = session.execute(text("SELECT COUNT(*) FROM categorias_menu WHERE nombre = :nombre"), {"nombre": nombre})
                count = result.fetchone()[0]
                
                if count == 0:
                    session.execute(text("""
                        INSERT INTO categorias_menu (nombre, descripcion, orden)
                        VALUES (:nombre, :descripcion, :orden)
                    """), {
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "orden": orden
                    })
                    print(f"✅ Categoría '{nombre}' insertada")
                else:
                    print(f"⚠️ Categoría '{nombre}' ya existe")
        
        except Exception as e:
            print(f"❌ Error insertando categorías: {e}")
        
        # 7. Insertar acompañamientos fijos por defecto
        print("\n🥗 Insertando acompañamientos fijos por defecto...")
        try:
            acompanamientos_default = [
                ("Plátano maduro", "Plátano maduro frito", 1),
                ("Arroz", "Arroz blanco", 2),
                ("Ensalada", "Ensalada fresca", 3),
                ("Sopa", "Sopa del día", 4),
                ("Bebida", "Bebida del día", 5)
            ]
            
            for nombre, descripcion, orden in acompanamientos_default:
                # Verificar si ya existe
                result = session.execute(text("SELECT COUNT(*) FROM acompanamientos_fijos WHERE nombre = :nombre"), {"nombre": nombre})
                count = result.fetchone()[0]
                
                if count == 0:
                    session.execute(text("""
                        INSERT INTO acompanamientos_fijos (nombre, descripcion, orden)
                        VALUES (:nombre, :descripcion, :orden)
                    """), {
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "orden": orden
                    })
                    print(f"✅ Acompañamiento '{nombre}' insertado")
                else:
                    print(f"⚠️ Acompañamiento '{nombre}' ya existe")
        
        except Exception as e:
            print(f"❌ Error insertando acompañamientos: {e}")
        
        # 8. Insertar platos de ejemplo
        print("\n🍽️ Insertando platos de ejemplo...")
        try:
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
                # Verificar si ya existe
                result = session.execute(text("SELECT COUNT(*) FROM platos_restaurante WHERE nombre = :nombre"), {"nombre": nombre})
                count = result.fetchone()[0]
                
                if count == 0:
                    session.execute(text("""
                        INSERT INTO platos_restaurante (nombre, descripcion, precio, tipo)
                        VALUES (:nombre, :descripcion, :precio, :tipo)
                    """), {
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "precio": precio,
                        "tipo": tipo
                    })
                    print(f"✅ Plato '{nombre}' insertado")
                else:
                    print(f"⚠️ Plato '{nombre}' ya existe")
        
        except Exception as e:
            print(f"❌ Error insertando platos: {e}")
        
        session.commit()
        session.close()
        
        print("\n🎉 Migración del sistema de menús del restaurante completada!")
        print("\n📊 Resumen de tablas creadas:")
        print("  - ✅ categorias_menu: Categorías de platos (Principio, Proteína)")
        print("  - ✅ platos_restaurante: Platos del restaurante")
        print("  - ✅ menu_dia: Menús del día")
        print("  - ✅ menu_categoria_platos: Relación menú-categoría-plato")
        print("  - ✅ acompanamientos_fijos: Acompañamientos que siempre se incluyen")
        print("\n🍽️ Datos de ejemplo insertados:")
        print("  - ✅ Categorías: Principio, Proteína")
        print("  - ✅ Acompañamientos fijos: Plátano, Arroz, Ensalada, Sopa, Bebida")
        print("  - ✅ Platos de ejemplo: Verduras, Frijoles, Pechuga, Carne, Hígado")
        print("  - ✅ Platos fijos: Frijolada, Chicharrón al barril")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_restaurant_menu_tables()


