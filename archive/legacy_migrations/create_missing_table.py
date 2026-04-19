#!/usr/bin/env python3
"""
Script para crear la tabla faltante menu_categoria_plato
"""
import sys
import os
from sqlalchemy import create_engine, text
from app.config import settings

def create_missing_table():
    """Crear la tabla menu_categoria_plato que falta"""
    print("🔧 Creando tabla faltante: menu_categoria_plato...")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            # Crear la tabla menu_categoria_plato
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS menu_categoria_plato (
                id SERIAL PRIMARY KEY,
                menu_dia_id INTEGER NOT NULL,
                categoria_id INTEGER NOT NULL,
                plato_id INTEGER NOT NULL,
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                FOREIGN KEY (menu_dia_id) REFERENCES menus_dia(id) ON DELETE CASCADE,
                FOREIGN KEY (categoria_id) REFERENCES categorias_menu(id) ON DELETE CASCADE,
                FOREIGN KEY (plato_id) REFERENCES platos_restaurante(id) ON DELETE CASCADE,
                UNIQUE(menu_dia_id, categoria_id, plato_id)
            );
            """
            
            print("📋 Creando tabla menu_categoria_plato...")
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
                
                # Contar registros
                result = conn.execute(text("SELECT COUNT(*) FROM menu_categoria_plato"))
                count = result.scalar()
                print(f"📊 Registros en la tabla: {count}")
                
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
    success = create_missing_table()
    if success:
        print("\n✅ Sistema listo para funcionar")
    else:
        print("\n❌ Hay problemas que necesitan ser corregidos")


