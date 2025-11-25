#!/usr/bin/env python3
"""
Script para corregir las categorías de platos de proteína que están mal asignadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.models.menu_restructured import CategoriaPlatoVariable, OpcionPlato

def corregir_categorias_proteinas():
    """Corregir las categorías de platos de proteína"""
    print("🔧 Corrigiendo categorías de platos de proteína...")
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # 1. Obtener la categoría "Proteína"
        categoria_proteina = db.query(CategoriaPlatoVariable).filter(
            CategoriaPlatoVariable.nombre == 'Proteína'
        ).first()
        
        if not categoria_proteina:
            print("❌ No se encontró la categoría 'Proteína'")
            return
        
        print(f"✅ Categoría 'Proteína' encontrada (ID: {categoria_proteina.id})")
        
        # 2. Lista de palabras clave que indican proteína
        palabras_proteina = [
            'pollo', 'cerdo', 'carne', 'pescado', 'res', 'pavo', 'pollo a la plancha',
            'cerdo en maracuyá', 'costillas', 'chuleta', 'chuzo', 'bistec', 'lomo',
            'pechuga', 'muslo', 'pierna', 'alitas', 'hamburguesa', 'salchicha'
        ]
        
        # 3. Buscar platos que deberían ser proteína pero están en "Principio"
        categoria_principio = db.query(CategoriaPlatoVariable).filter(
            CategoriaPlatoVariable.nombre == 'Principio'
        ).first()
        
        if not categoria_principio:
            print("❌ No se encontró la categoría 'Principio'")
            return
        
        print(f"🔍 Buscando platos mal categorizados en 'Principio' (ID: {categoria_principio.id})")
        
        # 4. Obtener todas las opciones que están en "Principio"
        opciones_mal_categorizadas = db.query(OpcionPlato).filter(
            OpcionPlato.categoria_id == categoria_principio.id
        ).all()
        
        platos_corregidos = []
        
        for opcion in opciones_mal_categorizadas:
            # Verificar si el nombre del plato contiene palabras de proteína
            nombre_lower = opcion.nombre.lower()
            es_proteina = any(palabra in nombre_lower for palabra in palabras_proteina)
            
            if es_proteina:
                print(f"   🔄 Corrigiendo: '{opcion.nombre}' -> Proteína")
                opcion.categoria_id = categoria_proteina.id
                platos_corregidos.append(opcion.nombre)
        
        # 5. Guardar cambios
        if platos_corregidos:
            db.commit()
            print(f"\n✅ Se corrigieron {len(platos_corregidos)} platos:")
            for plato in platos_corregidos:
                print(f"   - {plato}")
        else:
            print("\n✅ No se encontraron platos que necesiten corrección")
        
        # 6. Verificar resultado
        print("\n🔍 Verificando correcciones:")
        for opcion in opciones_mal_categorizadas:
            if opcion.nombre in platos_corregidos:
                categoria_actual = db.query(CategoriaPlatoVariable).filter(
                    CategoriaPlatoVariable.id == opcion.categoria_id
                ).first()
                print(f"   ✅ '{opcion.nombre}' -> '{categoria_actual.nombre}'")
        
        print(f"\n🎉 Corrección completada. {len(platos_corregidos)} platos ahora están en la categoría correcta.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    corregir_categorias_proteinas()

