#!/usr/bin/env python3
"""
Script de prueba para verificar que la aplicación funciona correctamente
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Iniciando Sistema POS...")
    print("📊 Verificando configuración...")
    
    # Verificar que la aplicación se puede importar
    try:
        from app.models import *
        print("✅ Modelos importados correctamente")
    except Exception as e:
        print(f"❌ Error importando modelos: {e}")
        exit(1)
    
    # Verificar configuración
    try:
        from app.config import settings
        print(f"✅ Configuración cargada: {settings.database_url}")
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        exit(1)
    
    print("🎯 Iniciando servidor...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
