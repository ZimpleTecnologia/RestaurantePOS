#!/usr/bin/env python3
"""
Script para crear categorías básicas para el sistema de menús
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Intentar importar settings de la aplicación
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))
    from config import settings as app_settings
    from database import Base
    print("✅ Configuración de la aplicación cargada.")
    sys.path.pop(0)
except ImportError as e:
    print(f"❌ Error importando configuración: {e}")
    app_settings = None
    Base = None

# Definir posibles URLs de conexión
DB_URLS = []

if app_settings and app_settings.database_url:
    DB_URLS.append(app_settings.database_url)

# Intentar diferentes configuraciones de PostgreSQL
pg_user = os.getenv("POSTGRES_USER", "postgres")
pg_password = os.getenv("POSTGRES_PASSWORD", "postgres")
pg_db = os.getenv("POSTGRES_DB", "restaurante_pos_db")

DB_URLS.extend([
    f"postgresql://{pg_user}:{pg_password}@db:5432/{pg_db}",
    f"postgresql://{pg_user}:{pg_password}@localhost:55432/{pg_db}",
    f"postgresql://{pg_user}:{pg_password}@localhost:5432/{pg_db}",
    f"postgresql://{pg_user}:{pg_password}@host.docker.internal:55432/{pg_db}",
    f"postgresql://{pg_user}:{pg_password}@host.docker.internal:5432/{pg_db}",
    "sqlite:///./restaurante_pos.db"
])

def crear_categorias_basicas():
    """Crear categorías básicas para el sistema de menús"""
    
    for db_url in DB_URLS:
        try:
            print(f"🔧 Intentando conectar a: {db_url}")
            engine = create_engine(db_url, pool_pre_ping=True)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            
            with SessionLocal() as db:
                # Verificar si ya existen categorías
                from app.models.restaurant_menu import CategoriaMenuRestaurante
                
                categorias_existentes = db.query(CategoriaMenuRestaurante).count()
                print(f"📊 Categorías existentes: {categorias_existentes}")
                
                if categorias_existentes > 0:
                    print("✅ Ya existen categorías en la base de datos")
                    # Mostrar las categorías existentes
                    categorias = db.query(CategoriaMenuRestaurante).all()
                    for cat in categorias:
                        print(f"   - {cat.nombre} (ID: {cat.id}, Activo: {cat.is_active})")
                    return True
                
                # Crear categorías básicas
                categorias_basicas = [
                    {"nombre": "Proteína", "descripcion": "Platos con proteína animal", "orden": 1},
                    {"nombre": "Acompañamiento", "descripcion": "Arroces, papas, ensaladas", "orden": 2},
                    {"nombre": "Principio", "descripcion": "Sopas y cremas", "orden": 3},
                    {"nombre": "Bebida", "descripcion": "Jugos, gaseosas, agua", "orden": 4},
                    {"nombre": "Postre", "descripcion": "Dulces y postres", "orden": 5}
                ]
                
                print("🔧 Creando categorías básicas...")
                for cat_data in categorias_basicas:
                    categoria = CategoriaMenuRestaurante(
                        nombre=cat_data["nombre"],
                        descripcion=cat_data["descripcion"],
                        orden=cat_data["orden"],
                        is_active=True
                    )
                    db.add(categoria)
                    print(f"   ✅ Creada: {cat_data['nombre']}")
                
                db.commit()
                print(f"🎉 Se crearon {len(categorias_basicas)} categorías básicas")
                return True
                
        except Exception as e:
            print(f"❌ Error con {db_url}: {e}")
            continue
    
    print("❌ No se pudo conectar a ninguna base de datos")
    return False

if __name__ == "__main__":
    print("🏗️ CREADOR DE CATEGORÍAS BÁSICAS")
    print("=" * 50)
    crear_categorias_basicas()

