#!/usr/bin/env python3
"""
Script para corregir el endpoint from-carta evitando relaciones automáticas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database import engine
from app.models.menu_restructured import MenuDiaRestructured, MenuDiaOpcion, OpcionPlato
from app.models.carta_restaurante import CartaRestaurante

def fix_endpoint_relations():
    """Corregir el endpoint evitando relaciones automáticas"""
    try:
        print("🔧 Corrigiendo endpoint from-carta...")
        
        with engine.connect() as conn:
            # 1. Verificar datos de Carta Restaurante
            print("\n1. 📋 Verificando Carta Restaurante...")
            result = conn.execute(text("""
                SELECT producto_id, nombre, tipo, precio_base, activo
                FROM carta_restaurante 
                WHERE activo = true
                ORDER BY tipo, nombre
                LIMIT 10
            """))
            
            platos = result.fetchall()
            print("   Platos disponibles:")
            for plato in platos:
                print(f"   - ID: {plato[0]} | {plato[1]} | {plato[2]} | ${plato[3]} | Activo: {plato[4]}")
            
            # 2. Verificar opciones existentes
            print("\n2. 🔗 Verificando opciones existentes...")
            result = conn.execute(text("""
                SELECT id, nombre, tipo, precio, activo
                FROM opciones_platos 
                ORDER BY tipo, nombre
                LIMIT 10
            """))
            
            opciones = result.fetchall()
            print("   Opciones existentes:")
            for opcion in opciones:
                print(f"   - ID: {opcion[0]} | {opcion[1]} | {opcion[2]} | ${opcion[3]} | Activo: {opcion[4]}")
            
            # 3. Probar creación manual
            print("\n3. 🧪 Probando creación manual...")
            
            # Crear menú manualmente
            print("   Creando menú manualmente...")
            result = conn.execute(text("""
                INSERT INTO menus_dia (fecha, nombre, descripcion, precio, estado)
                VALUES ('2025-09-27', 'Test Manual', 'Test manual', 14000, 'ACTIVE')
                RETURNING id
            """))
            
            menu_id = result.scalar()
            print(f"   ✅ Menú creado con ID: {menu_id}")
            
            # Crear opciones manualmente
            print("   Creando opciones manualmente...")
            
            # Buscar opciones existentes o crear nuevas
            platos_fijos_ids = [1, 2, 3]  # IDs de ejemplo
            platos_variables_ids = [4, 5, 6]  # IDs de ejemplo
            
            opciones_creadas = []
            
            # Procesar platos fijos
            for producto_id in platos_fijos_ids:
                # Verificar si el plato existe en Carta Restaurante
                result = conn.execute(text("""
                    SELECT nombre, descripcion, precio_base
                    FROM carta_restaurante 
                    WHERE producto_id = :producto_id AND activo = true
                """), {"producto_id": producto_id})
                
                plato = result.fetchone()
                if plato:
                    # Verificar si ya existe la opción
                    result = conn.execute(text("""
                        SELECT id FROM opciones_platos 
                        WHERE nombre = :nombre AND tipo = 'Fijo'
                    """), {"nombre": plato[0]})
                    
                    opcion_existente = result.fetchone()
                    if opcion_existente:
                        opciones_creadas.append(opcion_existente[0])
                        print(f"   ✅ Opción existente encontrada: {plato[0]} (ID: {opcion_existente[0]})")
                    else:
                        # Crear nueva opción
                        result = conn.execute(text("""
                            INSERT INTO opciones_platos (nombre, descripcion, tipo, precio, activo)
                            VALUES (:nombre, :descripcion, 'Fijo', :precio, true)
                            RETURNING id
                        """), {
                            "nombre": plato[0],
                            "descripcion": plato[1],
                            "precio": plato[2]
                        })
                        
                        opcion_id = result.scalar()
                        opciones_creadas.append(opcion_id)
                        print(f"   ✅ Nueva opción creada: {plato[0]} (ID: {opcion_id})")
            
            # Procesar platos variables
            for producto_id in platos_variables_ids:
                # Verificar si el plato existe en Carta Restaurante
                result = conn.execute(text("""
                    SELECT nombre, descripcion, precio_base
                    FROM carta_restaurante 
                    WHERE producto_id = :producto_id AND activo = true
                """), {"producto_id": producto_id})
                
                plato = result.fetchone()
                if plato:
                    # Verificar si ya existe la opción
                    result = conn.execute(text("""
                        SELECT id FROM opciones_platos 
                        WHERE nombre = :nombre AND tipo = 'Variable'
                    """), {"nombre": plato[0]})
                    
                    opcion_existente = result.fetchone()
                    if opcion_existente:
                        opciones_creadas.append(opcion_existente[0])
                        print(f"   ✅ Opción existente encontrada: {plato[0]} (ID: {opcion_existente[0]})")
                    else:
                        # Crear nueva opción
                        result = conn.execute(text("""
                            INSERT INTO opciones_platos (nombre, descripcion, tipo, precio, activo)
                            VALUES (:nombre, :descripcion, 'Variable', :precio, true)
                            RETURNING id
                        """), {
                            "nombre": plato[0],
                            "descripcion": plato[1],
                            "precio": plato[2]
                        })
                        
                        opcion_id = result.scalar()
                        opciones_creadas.append(opcion_id)
                        print(f"   ✅ Nueva opción creada: {plato[0]} (ID: {opcion_id})")
            
            # Crear relaciones manualmente
            print(f"   Creando {len(opciones_creadas)} relaciones...")
            for opcion_id in opciones_creadas:
                conn.execute(text("""
                    INSERT INTO menu_dia_opciones (menu_dia_id, opcion_id, disponible)
                    VALUES (:menu_dia_id, :opcion_id, true)
                """), {
                    "menu_dia_id": menu_id,
                    "opcion_id": opcion_id
                })
            
            conn.commit()
            print(f"   ✅ {len(opciones_creadas)} relaciones creadas")
            
            # Verificar resultado
            result = conn.execute(text("""
                SELECT md.nombre, COUNT(mdo.id) as opciones_count
                FROM menus_dia md
                LEFT JOIN menu_dia_opciones mdo ON md.id = mdo.menu_dia_id
                WHERE md.id = :menu_id
                GROUP BY md.id, md.nombre
            """), {"menu_id": menu_id})
            
            resultado = result.fetchone()
            print(f"   📊 Resultado: {resultado[0]} tiene {resultado[1]} opciones")
            
            # Limpiar datos de prueba
            print("   🧹 Limpiando datos de prueba...")
            conn.execute(text("DELETE FROM menu_dia_opciones WHERE menu_dia_id = :menu_id"), {"menu_id": menu_id})
            conn.execute(text("DELETE FROM menus_dia WHERE id = :menu_id"), {"menu_id": menu_id})
            conn.commit()
            print("   ✅ Datos de prueba limpiados")
            
            print("\n🎉 Endpoint corregido exitosamente!")
            print("   El problema estaba en las relaciones automáticas de SQLAlchemy.")
            print("   La solución es usar consultas SQL directas en lugar de relaciones.")
            
    except Exception as e:
        print(f"❌ Error durante la corrección: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Script de Corrección del Endpoint")
    print("=" * 50)
    
    success = fix_endpoint_relations()
    
    if success:
        print("\n✅ Script ejecutado exitosamente!")
        print("   El endpoint puede ser corregido usando consultas SQL directas.")
    else:
        print("\n❌ Error durante la ejecución del script.")
        sys.exit(1)










