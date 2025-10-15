#!/usr/bin/env python3
"""
Script para crear la tabla faltante menu_categoria_plato con las referencias correctas
"""
import sys
import os
from sqlalchemy import create_engine, text
from app.config import settings

def create_missing_table_fixed():
    """Crear la tabla menu_categoria_plato con las referencias correctas"""
    print("🔧 Creando tabla faltante: menu_categoria_plato (con referencias corregidas)...")
    print("=" * 70)
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # Crear la tabla menu_categoria_plato con las referencias correctas
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS menu_categoria_plato (
                id SERIAL PRIMARY KEY,
                menu_dia_id INTEGER NOT NULL,
                categoria_id INTEGER NOT NULL,
                plato_id INTEGER NOT NULL,
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                FOREIGN KEY (menu_dia_id) REFERENCES menus_dia(menu_id) ON DELETE CASCADE,
                FOREIGN KEY (categoria_id) REFERENCES categorias_menu(id) ON DELETE CASCADE,
                FOREIGN KEY (plato_id) REFERENCES platos_restaurante(id) ON DELETE CASCADE,
                UNIQUE(menu_dia_id, categoria_id, plato_id)
            );
            """
            
            print("📋 Creando tabla menu_categoria_plato...")
            print("🔑 Referencias:")
            print("   - menu_dia_id → menus_dia(menu_id)")
            print("   - categoria_id → categorias_menu(id)")
            print("   - plato_id → platos_restaurante(id)")
            
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ Tabla menu_categoria_plato creada exitosamente")
            
            # Verificar que la tabla fue creada
            print("\n🔍 Verificando que la tabla fue creada...")
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'menu_categoria_plato'
            """))
            
            if result.fetchone():
                print("✅ Tabla menu_categoria_plato existe")
                
                # Obtener estructura de la tabla creada
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'menu_categoria_plato'
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                print(f"\n📊 Estructura de la tabla creada:")
                for col in columns:
                    print(f"   - {col[0]} ({col[1]}) - Nullable: {col[2]} - Default: {col[3]}")
                
                # Contar registros
                result = conn.execute(text("SELECT COUNT(*) FROM menu_categoria_plato"))
                count = result.scalar()
                print(f"\n📊 Registros en la tabla: {count}")
                
            else:
                print("❌ Error: La tabla no fue creada")
                return False
            
            print("\n🎉 Tabla creada exitosamente!")
            print("💡 Ahora puedes probar los endpoints del sistema de menús")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        return False

if __name__ == "__main__":
    success = create_missing_table_fixed()
    if success:
        print("\n✅ Sistema listo para funcionar")
        print("🌐 Prueba los endpoints en: http://127.0.0.1:8000/docs")
    else:
        print("\n❌ Hay problemas que necesitan ser corregidos")


