#!/usr/bin/env python3
"""
Script para revisar y corregir TODAS las categorías de platos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.models.menu_restructured import CategoriaPlatoVariable, OpcionPlato

def revisar_y_corregir_todas_categorias():
    """Revisar y corregir todas las categorías de platos"""
    print("🔍 Revisando TODAS las categorías de platos...")
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # 1. Obtener todas las categorías disponibles
        categorias = db.query(CategoriaPlatoVariable).all()
        print(f"\n📋 Categorías disponibles:")
        for cat in categorias:
            print(f"   ID: {cat.id} - '{cat.nombre}'")
        
        # 2. Obtener todas las opciones
        opciones = db.query(OpcionPlato).all()
        print(f"\n🍽️ Revisando {len(opciones)} platos:")
        
        # 3. Definir reglas de categorización
        reglas_categorizacion = {
            'Proteína': {
                'palabras_clave': ['pollo', 'cerdo', 'carne', 'pescado', 'res', 'pavo', 'pollo a la plancha',
                                 'cerdo en maracuyá', 'costillas', 'chuleta', 'chuzo', 'bistec', 'lomo',
                                 'pechuga', 'muslo', 'pierna', 'alitas', 'hamburguesa', 'salchicha', 'pollo'],
                'exclusiones': ['papas', 'arroz', 'ensalada', 'verdura', 'sopa', 'crema']
            },
            'Principio': {
                'palabras_clave': ['sopa', 'crema', 'caldo', 'consomé', 'puré', 'guiso', 'estofado'],
                'exclusiones': ['pollo', 'cerdo', 'carne', 'pescado']
            },
            'Acompañamiento': {
                'palabras_clave': ['papas', 'arroz', 'ensalada', 'verdura', 'vegetal', 'frijoles', 'lentejas',
                                 'garbanzos', 'quinoa', 'pasta', 'espagueti', 'macarrones', 'papas criollas',
                                 'arroz blanco', 'ensalada verde', 'verduras salteadas'],
                'exclusiones': ['pollo', 'cerdo', 'carne', 'pescado']
            },
            'Bebida': {
                'palabras_clave': ['jugo', 'bebida', 'refresco', 'gaseosa', 'agua', 'limonada', 'naranjada',
                                 'jugo de naranja', 'jugo de limón', 'café', 'té', 'chocolate'],
                'exclusiones': []
            },
            'Postre': {
                'palabras_clave': ['postre', 'dulce', 'torta', 'helado', 'flan', 'mousse', 'tarta', 'pastel',
                                 'brownie', 'cheesecake', 'tiramisú'],
                'exclusiones': []
            }
        }
        
        # 4. Revisar cada plato y sugerir correcciones
        correcciones_necesarias = []
        
        for opcion in opciones:
            nombre_lower = opcion.nombre.lower()
            categoria_actual = opcion.categoria.nombre if opcion.categoria else "Sin categoría"
            
            print(f"\n🔍 Revisando: '{opcion.nombre}'")
            print(f"   Categoría actual: '{categoria_actual}'")
            
            # Buscar la categoría correcta según las reglas
            categoria_sugerida = None
            confianza = 0
            
            for categoria_nombre, reglas in reglas_categorizacion.items():
                puntuacion = 0
                
                # Verificar palabras clave
                for palabra in reglas['palabras_clave']:
                    if palabra in nombre_lower:
                        puntuacion += 1
                
                # Verificar exclusiones
                for exclusion in reglas['exclusiones']:
                    if exclusion in nombre_lower:
                        puntuacion -= 2  # Penalizar si contiene exclusiones
                
                if puntuacion > confianza:
                    confianza = puntuacion
                    categoria_sugerida = categoria_nombre
            
            if categoria_sugerida and categoria_sugerida != categoria_actual:
                print(f"   ⚠️  Sugerencia: '{categoria_sugerida}' (confianza: {confianza})")
                correcciones_necesarias.append({
                    'opcion': opcion,
                    'categoria_actual': categoria_actual,
                    'categoria_sugerida': categoria_sugerida,
                    'confianza': confianza
                })
            else:
                print(f"   ✅ Categoría correcta")
        
        # 5. Mostrar resumen de correcciones necesarias
        print(f"\n📊 Resumen de correcciones necesarias:")
        print(f"   Total platos revisados: {len(opciones)}")
        print(f"   Correcciones sugeridas: {len(correcciones_necesarias)}")
        
        if correcciones_necesarias:
            print(f"\n🔧 Correcciones sugeridas:")
            for correccion in correcciones_necesarias:
                print(f"   - '{correccion['opcion'].nombre}': '{correccion['categoria_actual']}' → '{correccion['categoria_sugerida']}' (confianza: {correccion['confianza']})")
            
            # 6. Aplicar correcciones automáticamente
            print(f"\n🤖 Aplicando correcciones automáticamente...")
            correcciones_aplicadas = 0
            
            for correccion in correcciones_necesarias:
                if correccion['confianza'] >= 1:  # Solo aplicar si hay confianza suficiente
                    # Buscar la categoría correcta
                    categoria_correcta = db.query(CategoriaPlatoVariable).filter(
                        CategoriaPlatoVariable.nombre == correccion['categoria_sugerida']
                    ).first()
                    
                    if categoria_correcta:
                        correccion['opcion'].categoria_id = categoria_correcta.id
                        print(f"   ✅ '{correccion['opcion'].nombre}' → '{correccion['categoria_sugerida']}'")
                        correcciones_aplicadas += 1
                    else:
                        print(f"   ❌ No se encontró la categoría '{correccion['categoria_sugerida']}'")
            
            # Guardar cambios
            if correcciones_aplicadas > 0:
                db.commit()
                print(f"\n🎉 Se aplicaron {correcciones_aplicadas} correcciones")
            else:
                print(f"\n⚠️  No se aplicaron correcciones automáticas")
        else:
            print(f"\n✅ ¡Todas las categorías están correctas!")
        
        # 7. Verificación final
        print(f"\n🔍 Verificación final por categoría:")
        for categoria in categorias:
            platos_en_categoria = db.query(OpcionPlato).filter(
                OpcionPlato.categoria_id == categoria.id
            ).all()
            
            print(f"\n📂 {categoria.nombre} ({len(platos_en_categoria)} platos):")
            for plato in platos_en_categoria:
                print(f"   - {plato.nombre}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    revisar_y_corregir_todas_categorias()
