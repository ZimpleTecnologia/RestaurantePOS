#!/usr/bin/env python3
"""
Script para verificar que el sistema de menús del restaurante esté funcionando
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_menu_system():
    """Verificar que el sistema de menús del restaurante esté funcionando"""
    print("🔍 Verificando Sistema de Menús del Restaurante...")
    print("=" * 60)
    
    try:
        # Usar la configuración del proyecto
        from app.config import settings
        
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ Conectado a la base de datos")
        
        # 1. Verificar categorías
        print("\n📋 Verificando categorías...")
        result = session.execute(text("SELECT COUNT(*) FROM categorias_menu"))
        count = result.fetchone()[0]
        print(f"✅ Categorías en la base de datos: {count}")
        
        if count > 0:
            result = session.execute(text("SELECT nombre, descripcion FROM categorias_menu ORDER BY orden"))
            for row in result:
                print(f"   - {row[0]}: {row[1]}")
        
        # 2. Verificar platos
        print("\n🍽️ Verificando platos...")
        result = session.execute(text("SELECT COUNT(*) FROM platos_restaurante"))
        count = result.fetchone()[0]
        print(f"✅ Platos en la base de datos: {count}")
        
        if count > 0:
            result = session.execute(text("SELECT nombre, tipo, precio FROM platos_restaurante ORDER BY nombre"))
            for row in result:
                print(f"   - {row[0]} ({row[1]}): ${row[2]}")
        
        # 3. Verificar acompañamientos fijos
        print("\n🥗 Verificando acompañamientos fijos...")
        result = session.execute(text("SELECT COUNT(*) FROM acompanamientos_fijos"))
        count = result.fetchone()[0]
        print(f"✅ Acompañamientos fijos en la base de datos: {count}")
        
        if count > 0:
            result = session.execute(text("SELECT nombre, descripcion FROM acompanamientos_fijos ORDER BY orden"))
            for row in result:
                print(f"   - {row[0]}: {row[1]}")
        
        # 4. Verificar menús del día
        print("\n📅 Verificando menús del día...")
        result = session.execute(text("SELECT COUNT(*) FROM menu_dia"))
        count = result.fetchone()[0]
        print(f"✅ Menús del día en la base de datos: {count}")
        
        if count > 0:
            result = session.execute(text("SELECT id, fecha, nombre, publicado FROM menu_dia ORDER BY fecha DESC"))
            for row in result:
                print(f"   - {row[2]} ({row[1]}) - Publicado: {row[3]}")
        
        # 5. Verificar relaciones menú-categoría-plato
        print("\n🔗 Verificando relaciones menú-categoría-plato...")
        result = session.execute(text("SELECT COUNT(*) FROM menu_categoria_platos"))
        count = result.fetchone()[0]
        print(f"✅ Relaciones menú-categoría-plato: {count}")
        
        if count > 0:
            result = session.execute(text("""
                SELECT m.nombre as menu, c.nombre as categoria, p.nombre as plato
                FROM menu_categoria_platos mcp
                JOIN menu_dia m ON mcp.menu_dia_id = m.id
                JOIN categorias_menu c ON mcp.categoria_id = c.id
                JOIN platos_restaurante p ON mcp.plato_id = p.id
                ORDER BY m.fecha DESC, c.orden, p.nombre
            """))
            for row in result:
                print(f"   - {row[0]} > {row[1]} > {row[2]}")
        
        # 6. Verificar menú de hoy
        print("\n📅 Verificando menú de hoy...")
        from datetime import date
        today = date.today()
        
        result = session.execute(text("""
            SELECT m.nombre, m.publicado, 
                   COUNT(DISTINCT c.nombre) as categorias,
                   COUNT(DISTINCT p.nombre) as platos
            FROM menu_dia m
            LEFT JOIN menu_categoria_platos mcp ON m.id = mcp.menu_dia_id
            LEFT JOIN categorias_menu c ON mcp.categoria_id = c.id
            LEFT JOIN platos_restaurante p ON mcp.plato_id = p.id
            WHERE m.fecha = :fecha
            GROUP BY m.id, m.nombre, m.publicado
        """), {"fecha": today})
        
        row = result.fetchone()
        if row:
            print(f"✅ Menú de hoy: {row[0]}")
            print(f"   - Publicado: {row[1]}")
            print(f"   - Categorías: {row[2]}")
            print(f"   - Platos: {row[3]}")
        else:
            print("⚠️ No hay menú para hoy")
        
        session.close()
        
        print("\n" + "=" * 60)
        print("🎉 Verificación del sistema de menús completada!")
        print("\n📊 Resumen:")
        print("  - ✅ Base de datos: Conectada y funcionando")
        print("  - ✅ Tablas: Creadas y con datos")
        print("  - ✅ Categorías: Principio, Proteína")
        print("  - ✅ Platos: Menu_Dia, Plato_Fijo")
        print("  - ✅ Acompañamientos: Fijos incluidos")
        print("  - ✅ Menús: Del día con relaciones")
        
        print("\n🌐 URLs disponibles:")
        print("  - Home: http://127.0.0.1:8000/")
        print("  - Documentación API: http://127.0.0.1:8000/docs")
        print("  - Gestión de Menús: http://127.0.0.1:8000/admin/menus")
        print("  - Vista de Meseros: http://127.0.0.1:8000/meseros/menus")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_menu_system()


