#!/usr/bin/env python3
"""
Script de migración para agregar columna categoria_id a la tabla platos_restaurante
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def add_categoria_id_column():
    """Agregar columna categoria_id a la tabla platos_restaurante"""
    print("🔧 Agregando columna categoria_id a la tabla platos_restaurante...")
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        inspector = inspect(engine)
        
        # Verificar columnas existentes
        columns = [col['name'] for col in inspector.get_columns('platos_restaurante')]
        print(f"\n📋 Columnas actuales en platos_restaurante: {', '.join(columns)}")
        
        # Agregar columna categoria_id si no existe
        if 'categoria_id' not in columns:
            print("\n➕ Agregando columna 'categoria_id'...")
            try:
                session.execute(text("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 
                            FROM information_schema.columns 
                            WHERE table_name = 'platos_restaurante' 
                            AND column_name = 'categoria_id'
                        ) THEN
                            ALTER TABLE platos_restaurante 
                            ADD COLUMN categoria_id INTEGER 
                            REFERENCES categorias_menu(id) 
                            ON DELETE SET NULL;
                            RAISE NOTICE 'Columna categoria_id agregada exitosamente';
                        ELSE
                            RAISE NOTICE 'Columna categoria_id ya existe';
                        END IF;
                    END $$;
                """))
                session.commit()
                print("✅ Columna 'categoria_id' agregada exitosamente")
            except Exception as e:
                session.rollback()
                print(f"❌ Error agregando columna 'categoria_id': {e}")
        else:
            print("ℹ️ Columna 'categoria_id' ya existe")
        
        # Verificar columnas después de la migración
        columns_after = [col['name'] for col in inspector.get_columns('platos_restaurante')]
        print(f"\n📋 Columnas finales en platos_restaurante: {', '.join(columns_after)}")
        
        session.close()
        
        print("\n🎉 Migración completada!")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    add_categoria_id_column()

