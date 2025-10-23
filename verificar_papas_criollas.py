#!/usr/bin/env python3
"""
Script específico para verificar el problema de Papas Criollas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.models.menu_restructured import CategoriaPlatoVariable, OpcionPlato

def verificar_papas_criollas():
    """Verificar específicamente el problema de Papas Criollas"""
    print("🥔 Verificando específicamente Papas Criollas...")
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # 1. Buscar Papas Criollas
        papas_criollas = db.query(OpcionPlato).filter(
            OpcionPlato.nombre.ilike('%papas criollas%')
        ).all()
        
        print(f"🔍 Encontradas {len(papas_criollas)} opciones con 'papas criollas':")
        for papas in papas_criollas:
            categoria_actual = papas.categoria.nombre if papas.categoria else "Sin categoría"
            print(f"   - '{papas.nombre}' (ID: {papas.id}) → Categoría: '{categoria_actual}' (ID: {papas.categoria_id})")
        
        # 2. Verificar todas las categorías disponibles
        print(f"\n📋 Categorías disponibles:")
        categorias = db.query(CategoriaPlatoVariable).all()
        for cat in categorias:
            print(f"   ID: {cat.id} - '{cat.nombre}'")
        
        # 3. Buscar la categoría "Acompañamiento"
        categoria_acompanamiento = db.query(CategoriaPlatoVariable).filter(
            CategoriaPlatoVariable.nombre == 'Acompañamiento'
        ).first()
        
        if categoria_acompanamiento:
            print(f"\n✅ Categoría 'Acompañamiento' encontrada (ID: {categoria_acompanamiento.id})")
            
            # 4. Corregir Papas Criollas si está mal categorizada
            for papas in papas_criollas:
                if papas.categoria_id != categoria_acompanamiento.id:
                    print(f"🔧 Corrigiendo '{papas.nombre}' de '{papas.categoria.nombre if papas.categoria else 'Sin categoría'}' a 'Acompañamiento'")
                    papas.categoria_id = categoria_acompanamiento.id
                else:
                    print(f"✅ '{papas.nombre}' ya está en la categoría correcta")
            
            # Guardar cambios
            db.commit()
            print(f"💾 Cambios guardados")
            
        else:
            print(f"❌ No se encontró la categoría 'Acompañamiento'")
        
        # 5. Verificación final
        print(f"\n🔍 Verificación final:")
        for papas in papas_criollas:
            db.refresh(papas)  # Recargar desde la base de datos
            categoria_final = papas.categoria.nombre if papas.categoria else "Sin categoría"
            print(f"   '{papas.nombre}' → '{categoria_final}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_papas_criollas()
