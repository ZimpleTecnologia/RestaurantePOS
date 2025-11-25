#!/usr/bin/env python3
"""
Script para verificar que las correcciones de categorías se aplicaron correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.models.menu_restructured import CategoriaPlatoVariable, OpcionPlato

def verificar_correcciones():
    """Verificar que las correcciones se aplicaron correctamente"""
    print("🔍 Verificando correcciones de categorías...")
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # 1. Obtener categorías
        categoria_proteina = db.query(CategoriaPlatoVariable).filter(
            CategoriaPlatoVariable.nombre == 'Proteína'
        ).first()
        
        categoria_principio = db.query(CategoriaPlatoVariable).filter(
            CategoriaPlatoVariable.nombre == 'Principio'
        ).first()
        
        print(f"📋 Categorías disponibles:")
        print(f"   - Proteína (ID: {categoria_proteina.id})")
        print(f"   - Principio (ID: {categoria_principio.id})")
        
        # 2. Verificar platos en cada categoría
        print(f"\n🥩 Platos en categoría 'Proteína':")
        platos_proteina = db.query(OpcionPlato).filter(
            OpcionPlato.categoria_id == categoria_proteina.id
        ).all()
        
        for plato in platos_proteina:
            print(f"   ✅ {plato.nombre}")
        
        print(f"\n🥗 Platos en categoría 'Principio':")
        platos_principio = db.query(OpcionPlato).filter(
            OpcionPlato.categoria_id == categoria_principio.id
        ).all()
        
        for plato in platos_principio:
            print(f"   ✅ {plato.nombre}")
        
        # 3. Verificar platos sin categoría
        print(f"\n❓ Platos sin categoría:")
        platos_sin_categoria = db.query(OpcionPlato).filter(
            OpcionPlato.categoria_id.is_(None)
        ).all()
        
        for plato in platos_sin_categoria:
            print(f"   ⚠️  {plato.nombre}")
        
        # 4. Estadísticas finales
        total_platos = db.query(OpcionPlato).count()
        platos_con_categoria = db.query(OpcionPlato).filter(
            OpcionPlato.categoria_id.isnot(None)
        ).count()
        
        print(f"\n📊 Estadísticas finales:")
        print(f"   Total platos: {total_platos}")
        print(f"   Con categoría: {platos_con_categoria}")
        print(f"   Sin categoría: {total_platos - platos_con_categoria}")
        print(f"   En Proteína: {len(platos_proteina)}")
        print(f"   En Principio: {len(platos_principio)}")
        
        # 5. Verificar que no hay platos de proteína en "Principio"
        palabras_proteina = ['pollo', 'cerdo', 'carne', 'pescado', 'res', 'pavo']
        platos_mal_categorizados = []
        
        for plato in platos_principio:
            nombre_lower = plato.nombre.lower()
            if any(palabra in nombre_lower for palabra in palabras_proteina):
                platos_mal_categorizados.append(plato.nombre)
        
        if platos_mal_categorizados:
            print(f"\n⚠️  Aún hay platos de proteína en 'Principio':")
            for plato in platos_mal_categorizados:
                print(f"   - {plato}")
        else:
            print(f"\n✅ ¡Perfecto! No hay platos de proteína mal categorizados en 'Principio'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verificar_correcciones()

