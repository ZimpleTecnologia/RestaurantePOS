#!/usr/bin/env python3
"""
Script para inicializar la configuración del sistema
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db, create_tables
from app.models.settings import SystemSettings
from sqlalchemy.orm import Session

def init_settings():
    """Inicializar configuración del sistema"""
    print("🔧 Inicializando configuración del sistema...")
    
    # Crear tablas si no existen
    create_tables()
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Verificar si ya existe configuración
        existing_settings = db.query(SystemSettings).first()
        
        if existing_settings:
            print("✅ Configuración del sistema ya existe")
            return
        
        # Crear configuración por defecto
        default_settings = SystemSettings(
            company_name="Mi Empresa",
            app_title="Sistema POS",
            app_subtitle="Punto de Venta",
            currency="USD",
            timezone="UTC-5",
            primary_color="#667eea",
            secondary_color="#764ba2",
            accent_color="#28a745",
            sidebar_color="#667eea",
            print_header="Mi Empresa\nDirección de la empresa\nTel: (123) 456-7890",
            print_footer="¡Gracias por su compra!\nVuelva pronto",
            enable_notifications=True,
            low_stock_threshold=10
        )
        
        db.add(default_settings)
        db.commit()
        
        print("✅ Configuración del sistema inicializada exitosamente")
        print(f"   - Nombre de empresa: {default_settings.company_name}")
        print(f"   - Moneda: {default_settings.currency}")
        print(f"   - Tema: Azul Clásico")
        
    except Exception as e:
        print(f"❌ Error inicializando configuración: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_settings()
