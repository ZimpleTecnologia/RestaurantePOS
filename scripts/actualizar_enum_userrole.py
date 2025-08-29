#!/usr/bin/env python3
"""
Script para actualizar el enum userrole en la base de datos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from sqlalchemy import text

def update_userrole_enum():
    """Actualizar el enum userrole en la base de datos"""
    db = SessionLocal()
    
    try:
        print("🔄 Actualizando enum userrole en la base de datos...")
        
        # Verificar valores actuales del enum
        result = db.execute(text("""
            SELECT unnest(enum_range(NULL::userrole)) as enum_value;
        """))
        current_values = [row[0] for row in result]
        print(f"Valores actuales del enum: {current_values}")
        
        # Valores que deberían estar en el enum
        required_values = ['ADMIN', 'MESERO', 'COCINA', 'CAJA', 'ALMACEN', 'SUPERVISOR']
        
        # Agregar valores faltantes
        for value in required_values:
            if value not in current_values:
                print(f"Agregando valor '{value}' al enum...")
                try:
                    db.execute(text(f"ALTER TYPE userrole ADD VALUE '{value}'"))
                    print(f"✅ Valor '{value}' agregado exitosamente")
                except Exception as e:
                    print(f"⚠️  Error agregando '{value}': {e}")
        
        # Confirmar cambios
        db.commit()
        
        # Verificar valores finales
        result = db.execute(text("""
            SELECT unnest(enum_range(NULL::userrole)) as enum_value ORDER BY enum_value;
        """))
        final_values = [row[0] for row in result]
        print(f"Valores finales del enum: {final_values}")
        
        print("✅ Enum userrole actualizado exitosamente")
        
    except Exception as e:
        print(f"❌ Error actualizando enum: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_userrole_enum()
