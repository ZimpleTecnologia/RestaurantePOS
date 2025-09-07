#!/usr/bin/env python3
"""
Script para crear nueva tabla de configuraciones
"""
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import get_db, engine

def create_new_settings_table():
    """Crear nueva tabla de configuraciones"""
    print("🔧 Creando nueva tabla de configuraciones...")
    
    db = next(get_db())
    
    try:
        # 1. Crear nueva tabla con estructura correcta
        print("\n1️⃣ Creando tabla system_settings_new...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS system_settings_new (
            id SERIAL PRIMARY KEY,
            setting_key VARCHAR(100) UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.execute(text(create_table_sql))
        print("✅ Tabla system_settings_new creada")
        
        # 2. Insertar configuraciones por defecto
        print("\n2️⃣ Insertando configuraciones por defecto...")
        
        default_settings = [
            ("cash_register_password", "1234", "Contraseña para acceso al módulo de caja"),
            ("cash_register_name", "Caja Principal", "Nombre de la caja registradora"),
            ("tax_rate", "19.0", "Porcentaje de impuestos (IVA)"),
            ("currency", "COP", "Moneda del sistema"),
            ("business_name", "Mi Restaurante", "Nombre del negocio"),
            ("business_address", "", "Dirección del negocio"),
            ("business_phone", "", "Teléfono del negocio"),
            ("business_email", "", "Email del negocio"),
            ("receipt_footer", "¡Gracias por su visita!", "Pie de página para recibos"),
            ("auto_backup", "true", "Respaldo automático (true/false)"),
            ("session_timeout", "30", "Tiempo de sesión en minutos"),
            ("max_discount", "20.0", "Descuento máximo permitido (%)"),
            ("require_cash_register", "true", "Requiere caja abierta para ventas (true/false)")
        ]
        
        for key, value, description in default_settings:
            insert_sql = """
            INSERT INTO system_settings_new (setting_key, setting_value, description)
            VALUES (:key, :value, :description)
            ON CONFLICT (setting_key) DO NOTHING;
            """
            
            db.execute(text(insert_sql), {
                "key": key,
                "value": value,
                "description": description
            })
        
        print(f"✅ {len(default_settings)} configuraciones insertadas")
        
        # 3. Renombrar tablas
        print("\n3️⃣ Renombrando tablas...")
        
        # Hacer backup de la tabla antigua
        db.execute(text("DROP TABLE IF EXISTS system_settings_backup"))
        db.execute(text("ALTER TABLE system_settings RENAME TO system_settings_backup"))
        
        # Renombrar nueva tabla
        db.execute(text("ALTER TABLE system_settings_new RENAME TO system_settings"))
        
        print("✅ Tabla antigua respaldada como system_settings_backup")
        print("✅ Nueva tabla activa como system_settings")
        
        # 4. Verificar configuraciones
        print("\n4️⃣ Verificando configuraciones...")
        
        result = db.execute(text("SELECT setting_key, setting_value FROM system_settings"))
        settings = result.fetchall()
        
        print(f"✅ {len(settings)} configuraciones encontradas:")
        for setting in settings:
            print(f"   - {setting[0]}: {setting[1]}")
        
        db.commit()
        
        print("\n✅ Nueva tabla de configuraciones creada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

def main():
    """Función principal"""
    print("=" * 70)
    print("🔧 CREACIÓN DE NUEVA TABLA DE CONFIGURACIONES")
    print("=" * 70)
    
    create_new_settings_table()
    
    print("\n" + "=" * 70)
    print("✅ Proceso completado")

if __name__ == "__main__":
    main()
