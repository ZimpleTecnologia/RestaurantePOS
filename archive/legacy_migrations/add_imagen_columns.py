#!/usr/bin/env python3
"""
Script de migración para agregar columnas de imagen a la tabla platos_restaurante
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

def add_imagen_columns():
    """Agregar columnas de imagen a la tabla platos_restaurante"""
    print("🔧 Agregando columnas de imagen a la tabla platos_restaurante...")
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        inspector = inspect(engine)
        
        # Verificar columnas existentes
        columns = [col['name'] for col in inspector.get_columns('platos_restaurante')]
        print(f"\n📋 Columnas actuales en platos_restaurante: {', '.join(columns)}")
        
        # Agregar columna imagen_data si no existe (usando DO block para verificar)
        print("\n➕ Verificando y agregando columna 'imagen_data'...")
        try:
            session.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'platos_restaurante' 
                        AND column_name = 'imagen_data'
                    ) THEN
                        ALTER TABLE platos_restaurante ADD COLUMN imagen_data BYTEA;
                        RAISE NOTICE 'Columna imagen_data agregada exitosamente';
                    ELSE
                        RAISE NOTICE 'Columna imagen_data ya existe';
                    END IF;
                END $$;
            """))
            session.commit()
            print("✅ Verificación de columna 'imagen_data' completada")
        except Exception as e:
            session.rollback()
            print(f"❌ Error verificando columna 'imagen_data': {e}")
        
        # Agregar columna imagen_tipo si no existe (usando DO block para verificar)
        print("\n➕ Verificando y agregando columna 'imagen_tipo'...")
        try:
            session.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'platos_restaurante' 
                        AND column_name = 'imagen_tipo'
                    ) THEN
                        ALTER TABLE platos_restaurante ADD COLUMN imagen_tipo VARCHAR(50);
                        RAISE NOTICE 'Columna imagen_tipo agregada exitosamente';
                    ELSE
                        RAISE NOTICE 'Columna imagen_tipo ya existe';
                    END IF;
                END $$;
            """))
            session.commit()
            print("✅ Verificación de columna 'imagen_tipo' completada")
        except Exception as e:
            session.rollback()
            print(f"❌ Error verificando columna 'imagen_tipo': {e}")
        
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
    add_imagen_columns()

