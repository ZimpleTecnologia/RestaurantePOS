#!/usr/bin/env python3
"""
Script para diagnosticar el problema de categorías trocadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.models.menu_restructured import CategoriaPlatoVariable, OpcionPlato

def diagnosticar_categorias():
    """Diagnosticar el problema de categorías"""
    print("🔍 Diagnosticando categorías...")
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # 1. Verificar categorías existentes
        print("\n📋 Categorías disponibles:")
        categorias = db.query(CategoriaPlatoVariable).all()
        for cat in categorias:
            print(f"   ID: {cat.id}, Nombre: '{cat.nombre}', Activo: {cat.activo}")
        
        # 2. Verificar opciones y sus categorías
        print("\n🍽️ Opciones de platos y sus categorías:")
        opciones = db.query(OpcionPlato).all()
        for opcion in opciones:
            categoria_nombre = opcion.categoria.nombre if opcion.categoria else "Sin categoría"
            print(f"   '{opcion.nombre}' (ID: {opcion.id}) -> Categoría: '{categoria_nombre}' (ID: {opcion.categoria_id})")
        
        # 3. Verificar si hay categorías duplicadas o incorrectas
        print("\n🔍 Verificando categorías problemáticas:")
        
        # Buscar categorías que podrían estar mal asignadas
        categorias_principio = db.query(CategoriaPlatoVariable).filter(
            CategoriaPlatoVariable.nombre.ilike('%principio%')
        ).all()
        
        categorias_proteina = db.query(CategoriaPlatoVariable).filter(
            CategoriaPlatoVariable.nombre.ilike('%proteína%')
        ).all()
        
        print(f"   Categorías con 'principio': {[c.nombre for c in categorias_principio]}")
        print(f"   Categorías con 'proteína': {[c.nombre for c in categorias_proteina]}")
        
        # 4. Verificar platos que deberían ser proteína pero están en principio
        print("\n🥩 Platos que podrían estar mal categorizados:")
        platos_proteinas = ['pollo', 'cerdo', 'carne', 'pescado', 'res', 'pavo']
        
        for opcion in opciones:
            if opcion.categoria and any(proteina in opcion.nombre.lower() for proteina in platos_proteinas):
                if 'principio' in opcion.categoria.nombre.lower():
                    print(f"   ⚠️  '{opcion.nombre}' está en categoría '{opcion.categoria.nombre}' pero parece ser proteína")
        
        # 5. Estadísticas
        print(f"\n📊 Estadísticas:")
        print(f"   Total categorías: {len(categorias)}")
        print(f"   Total opciones: {len(opciones)}")
        print(f"   Opciones con categoría: {len([o for o in opciones if o.categoria])}")
        print(f"   Opciones sin categoría: {len([o for o in opciones if not o.categoria])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    diagnosticar_categorias()

