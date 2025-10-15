#!/usr/bin/env python3
"""
Script para crear las categorías básicas del sistema de menús usando SQL directo
"""
import os
import sys
from sqlalchemy import create_engine, text
from app.config import settings

def create_basic_categories():
    """Crear categorías básicas usando SQL directo"""
    try:
        print("🔧 Creando categorías básicas del sistema de menús...")

        # Conectar usando la configuración del proyecto
        engine = create_engine(settings.database_url)

        with engine.connect() as conn:
            # Verificar si ya existen categorías
            result = conn.execute(text("SELECT COUNT(*) FROM categorias_menu"))
            count = result.scalar()

            if count > 0:
                print(f"ℹ️ Ya existen {count} categorías en la base de datos")
                result = conn.execute(text("SELECT nombre FROM categorias_menu ORDER BY orden"))
                categorias = result.fetchall()
                print("📋 Categorías existentes:")
                for cat in categorias:
                    print(f"   - {cat[0]}")
                return True

            # Crear categorías básicas
            categorias_basicas = [
                ("Principio", "Platos de entrada o principio", 1),
                ("Proteína", "Platos principales con proteína", 2)
            ]

            print("📋 Creando categorías básicas...")
            for nombre, descripcion, orden in categorias_basicas:
                try:
                    conn.execute(text("""
                        INSERT INTO categorias_menu (nombre, descripcion, orden, is_active)
                        VALUES (:nombre, :descripcion, :orden, true)
                    """), {
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "orden": orden
                    })
                    print(f"✅ Categoría '{nombre}' creada")
                except Exception as e:
                    print(f"⚠️ Error creando categoría '{nombre}': {e}")

            conn.commit()
            print("\n🎉 Categorías básicas creadas exitosamente!")
            # Verificar resultado
            result = conn.execute(text("SELECT COUNT(*) FROM categorias_menu"))
            total = result.scalar()
            print(f"📊 Total de categorías en la base de datos: {total}")

            return True

    except Exception as e:
        print(f"❌ Error creando categorías: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_basic_categories()
    if success:
        print("\n✅ Script ejecutado exitosamente")
        print("🌐 Ahora puedes probar el modal de opciones de platos")
        print("   Las categorías deberían aparecer en el dropdown")
        print("   URL: http://127.0.0.1:8000/admin/menus")
    else:
        print("\n❌ Error ejecutando el script")
        sys.exit(1)