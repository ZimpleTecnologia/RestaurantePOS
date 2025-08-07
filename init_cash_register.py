#!/usr/bin/env python3
"""
Script para inicializar el sistema de caja con datos por defecto
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, create_tables
from app.models.cash_register import CashRegister
from app.models.user import User

def init_cash_register():
    """Inicializar sistema de caja con datos por defecto"""
    print("🔧 Inicializando sistema de caja...")
    
    # Crear tablas si no existen
    create_tables()
    
    db = SessionLocal()
    try:
        # Verificar si ya existe una caja registradora
        existing_register = db.query(CashRegister).first()
        
        if existing_register:
            print("✅ Sistema de caja ya inicializado")
            print(f"   Caja existente: {existing_register.name} ({existing_register.register_number})")
            return
        
        # Crear caja registradora por defecto
        default_register = CashRegister(
            register_number="CAJA-001",
            name="Caja Principal",
            description="Caja registradora principal del negocio",
            is_active=True
        )
        
        db.add(default_register)
        db.commit()
        db.refresh(default_register)
        
        print("✅ Sistema de caja inicializado correctamente")
        print(f"   Caja creada: {default_register.name} ({default_register.register_number})")
        
        # Verificar que hay usuarios en el sistema
        users = db.query(User).all()
        if not users:
            print("⚠️  No hay usuarios en el sistema. Cree un usuario antes de usar el sistema de caja.")
        else:
            print(f"✅ {len(users)} usuario(s) encontrado(s) en el sistema")
        
    except Exception as e:
        print(f"❌ Error al inicializar sistema de caja: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_cash_register()
