#!/usr/bin/env python3
"""
Script para ejecutar la migración del sistema de menú del día
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

# Ejecutar la migración
if __name__ == "__main__":
    from migrate_menu_system import main
    main()


