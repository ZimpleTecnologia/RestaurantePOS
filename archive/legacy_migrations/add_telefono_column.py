"""
Script de migración para agregar columna telefono a users
"""
from sqlalchemy import create_engine, text
from app.config import settings

def add_telefono_column():
    """Agrega la columna telefono a la tabla users"""
    print("🔧 Ejecutando migración: agregar columna telefono...")
    
    # Crear engine
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as conn:
            # Agregar columna telefono
            conn.execute(text("""
                ALTER TABLE users ADD COLUMN IF NOT EXISTS telefono VARCHAR(20);
            """))
            conn.commit()
            
            print("✅ Columna 'telefono' agregada exitosamente a la tabla 'users'")
            
            # Verificar
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'telefono';
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ Verificación exitosa: {row}")
            else:
                print("⚠️  No se pudo verificar la columna")
                
    except Exception as e:
        print(f"❌ Error en la migración: {str(e)}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    add_telefono_column()
    print("✅ Migración completada")

