#!/usr/bin/env python3
"""
Script simple para probar los endpoints directamente
"""

import sys
import os
from sqlalchemy.orm import Session

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.carta_restaurante import CartaRestaurante

def test_direct_data():
    """Probar los datos directamente desde la base de datos"""
    print("🔍 Probando Datos Directamente desde Base de Datos")
    print("=" * 60)
    
    try:
        # Obtener sesión de base de datos
        db = next(get_db())
        
        # 1. Probar platos fijos
        print("\n1. 🍽️  Platos Fijos desde Carta Restaurante:")
        platos_fijos = db.query(CartaRestaurante).filter(
            CartaRestaurante.tipo == 'Fijo',
            CartaRestaurante.activo == True
        ).all()
        
        print(f"   📊 Total: {len(platos_fijos)}")
        for plato in platos_fijos[:3]:
            print(f"   ✅ {plato.nombre} - ${plato.precio_base:,.0f} COP")
        
        # 2. Probar platos variables
        print("\n2. 🔄 Platos Variables desde Carta Restaurante:")
        platos_variables = db.query(CartaRestaurante).filter(
            CartaRestaurante.tipo == 'Variable',
            CartaRestaurante.activo == True
        ).all()
        
        print(f"   📊 Total: {len(platos_variables)}")
        for plato in platos_variables[:3]:
            print(f"   ✅ {plato.nombre} - ${plato.precio_base:,.0f} COP")
        
        # 3. Verificar estructura de datos
        print("\n3. 🔍 Estructura de Datos:")
        if platos_fijos:
            plato_ejemplo = platos_fijos[0]
            print(f"   📋 Campos disponibles:")
            print(f"      - producto_id: {plato_ejemplo.producto_id}")
            print(f"      - nombre: {plato_ejemplo.nombre}")
            print(f"      - precio_base: {plato_ejemplo.precio_base}")
            print(f"      - tipo: {plato_ejemplo.tipo}")
            print(f"      - activo: {plato_ejemplo.activo}")
            print(f"      - categoria: {plato_ejemplo.categoria}")
        
        print("\n" + "=" * 60)
        print("✅ Datos disponibles correctamente")
        print("🎯 El problema podría estar en el JavaScript o en la conexión al servidor")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = test_direct_data()
    if not success:
        print("\n❌ Error en la prueba de datos")
        sys.exit(1)
    else:
        print("\n✅ Prueba de datos exitosa")
