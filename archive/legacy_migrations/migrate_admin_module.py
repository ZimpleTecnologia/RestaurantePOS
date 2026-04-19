"""
Script completo de migración para el Módulo de Administración
Ejecuta todas las migraciones necesarias para crear las tablas y columnas
"""
from sqlalchemy import create_engine, text
from app.config import settings

def run_migrations():
    """Ejecuta todas las migraciones del módulo de administración"""
    print("🚀 Iniciando migraciones del Módulo de Administración...")
    
    engine = create_engine(settings.database_url)
    
    migrations = [
        ("Agregar columna telefono", """
            ALTER TABLE users ADD COLUMN IF NOT EXISTS telefono VARCHAR(20);
        """),
        
        ("Crear tabla mesas", """
            CREATE TABLE IF NOT EXISTS mesas (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                numero INTEGER NOT NULL UNIQUE,
                capacidad INTEGER,
                estado BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE
            );
        """),
        
        ("Crear tabla permisos", """
            CREATE TABLE IF NOT EXISTS permisos (
                id SERIAL PRIMARY KEY,
                codigo VARCHAR(50) NOT NULL UNIQUE,
                nombre VARCHAR(100) NOT NULL,
                descripcion VARCHAR(255),
                modulo VARCHAR(50) NOT NULL,
                estado BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE
            );
        """),
        
        ("Crear tabla usuario_permiso", """
            CREATE TABLE IF NOT EXISTS usuario_permiso (
                usuario_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                permiso_id INTEGER NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (usuario_id, permiso_id)
            );
        """),
        
        ("Crear índices", """
            CREATE INDEX IF NOT EXISTS idx_permisos_codigo ON permisos(codigo);
            CREATE INDEX IF NOT EXISTS idx_permisos_modulo ON permisos(modulo);
            CREATE INDEX IF NOT EXISTS idx_mesas_numero ON mesas(numero);
            CREATE INDEX IF NOT EXISTS idx_mesas_estado ON mesas(estado);
            CREATE INDEX IF NOT EXISTS idx_usuario_permiso_usuario ON usuario_permiso(usuario_id);
            CREATE INDEX IF NOT EXISTS idx_usuario_permiso_permiso ON usuario_permiso(permiso_id);
        """)
    ]
    
    try:
        with engine.connect() as conn:
            for name, sql in migrations:
                print(f"📝 Ejecutando: {name}...")
                conn.execute(text(sql))
                conn.commit()
                print(f"   ✅ {name} - OK")
            
            print("\n🔍 Verificando tablas creadas...")
            
            # Verificar tablas
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('mesas', 'permisos', 'usuario_permiso')
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"   Tablas encontradas: {', '.join(tables)}")
            
            # Verificar columna telefono
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'telefono';
            """))
            
            row = result.fetchone()
            if row:
                print(f"   ✅ Columna telefono: {row[1]}")
            
            # Contar registros
            result = conn.execute(text("""
                SELECT 
                    (SELECT COUNT(*) FROM mesas) as mesas,
                    (SELECT COUNT(*) FROM permisos) as permisos,
                    (SELECT COUNT(*) FROM usuario_permiso) as usuario_permiso;
            """))
            
            counts = result.fetchone()
            print(f"\n📊 Registros actuales:")
            print(f"   - Mesas: {counts[0]}")
            print(f"   - Permisos: {counts[1]}")
            print(f"   - Usuario-Permiso: {counts[2]}")
            
        print("\n✅ Todas las migraciones completadas exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {str(e)}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_migrations()
    print("\n🎉 Proceso de migración finalizado")
    print("\n📌 Próximo paso: ejecutar 'python seed_permisos.py' para poblar permisos iniciales")

