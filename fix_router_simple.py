#!/usr/bin/env python3
"""
Script simple para arreglar el router
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_router():
    """Arreglar el router eliminando código duplicado"""
    try:
        print("🔧 Arreglando router menu_restructured.py...")
        
        # Leer el archivo
        with open('app/routers/menu_restructured.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Encontrar dónde empieza el problema (línea 797)
        problem_start = None
        for i, line in enumerate(lines):
            if '}")' in line and i > 790:
                problem_start = i
                break
        
        if problem_start:
            print(f"   Problema encontrado en línea {problem_start + 1}")
            
            # Encontrar dónde termina el endpoint original
            # Buscar la siguiente función o el final del archivo
            end_line = len(lines)
            for i in range(problem_start + 1, len(lines)):
                if lines[i].strip().startswith('@router.') or lines[i].strip().startswith('def '):
                    end_line = i
                    break
            
            print(f"   Eliminando líneas {problem_start + 1} a {end_line}")
            
            # Crear nuevo contenido
            new_lines = lines[:problem_start]
            
            # Agregar el endpoint corregido
            new_endpoint = '''@router.post("/menus/from-carta/")
def create_menu_from_carta(
    fecha: str,
    nombre: str,
    descripcion: str = "",
    precio: float = 0.0,
    platos_fijos_ids: str = "",
    platos_variables_ids: str = "",
    db: Session = Depends(get_db)
):
    """Crear nuevo menú del día desde Carta Restaurante usando consultas SQL directas"""
    try:
        from datetime import datetime
        
        print(f"🔍 Creando menú desde Carta Restaurante:")
        print(f"   Fecha: {fecha}")
        print(f"   Nombre: {nombre}")
        print(f"   Precio: {precio}")
        print(f"   Platos fijos IDs: {platos_fijos_ids}")
        print(f"   Platos variables IDs: {platos_variables_ids}")
        
        # Crear el menú usando consulta SQL directa
        result = db.execute(text("""
            INSERT INTO menus_dia (fecha, nombre, descripcion, precio, estado)
            VALUES (:fecha, :nombre, :descripcion, :precio, 'ACTIVE')
            RETURNING id
        """), {
            "fecha": datetime.strptime(fecha, '%Y-%m-%d').date(),
            "nombre": nombre,
            "descripcion": descripcion,
            "precio": precio
        })
        
        menu_id = result.scalar()
        print(f"✅ Menú creado con ID: {menu_id}")
        
        # Crear opciones desde Carta Restaurante
        opciones_creadas = []
        
        # Procesar platos fijos
        if platos_fijos_ids:
            platos_fijos_list = [int(id.strip()) for id in platos_fijos_ids.split(',') if id.strip()]
            print(f"🍽️ Procesando {len(platos_fijos_list)} platos fijos")
            
            for producto_id in platos_fijos_list:
                result = db.execute(text("""
                    SELECT nombre, descripcion, precio_base
                    FROM carta_restaurante 
                    WHERE producto_id = :producto_id AND activo = true
                """), {"producto_id": producto_id})
                
                plato = result.fetchone()
                if plato:
                    # Verificar si ya existe la opción
                    result = db.execute(text("""
                        SELECT id FROM opciones_platos 
                        WHERE nombre = :nombre AND tipo = 'Fijo'
                    """), {"nombre": plato[0]})
                    
                    opcion_existente = result.fetchone()
                    if opcion_existente:
                        opciones_creadas.append(opcion_existente[0])
                    else:
                        # Crear nueva opción
                        result = db.execute(text("""
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
        
        # Procesar platos variables
        if platos_variables_ids:
            platos_variables_list = [int(id.strip()) for id in platos_variables_ids.split(',') if id.strip()]
            print(f"🔄 Procesando {len(platos_variables_list)} platos variables")
            
            for producto_id in platos_variables_list:
                result = db.execute(text("""
                    SELECT nombre, descripcion, precio_base
                    FROM carta_restaurante 
                    WHERE producto_id = :producto_id AND activo = true
                """), {"producto_id": producto_id})
                
                plato = result.fetchone()
                if plato:
                    # Verificar si ya existe la opción
                    result = db.execute(text("""
                        SELECT id FROM opciones_platos 
                        WHERE nombre = :nombre AND tipo = 'Variable'
                    """), {"nombre": plato[0]})
                    
                    opcion_existente = result.fetchone()
                    if opcion_existente:
                        opciones_creadas.append(opcion_existente[0])
                    else:
                        # Crear nueva opción
                        result = db.execute(text("""
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
        
        # Crear relaciones
        print(f"📋 Creando {len(opciones_creadas)} relaciones...")
        for opcion_id in opciones_creadas:
            db.execute(text("""
                INSERT INTO menu_dia_opciones (menu_dia_id, opcion_id, disponible)
                VALUES (:menu_dia_id, :opcion_id, true)
            """), {
                "menu_dia_id": menu_id,
                "opcion_id": opcion_id
            })
        
        db.commit()
        print(f"✅ {len(opciones_creadas)} relaciones creadas")
        
        return {
            "success": True,
            "message": "Menú creado exitosamente desde Carta Restaurante",
            "menu": {
                "id": menu_id,
                "fecha": fecha,
                "nombre": nombre,
                "precio": float(precio),
                "estado": "ACTIVE"
            },
            "opciones_agregadas": len(opciones_creadas)
        }
        
    except Exception as e:
        print(f"❌ Error al crear menú: {str(e)}")
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Error al crear el menú desde Carta Restaurante"
        }

'''
            
            new_lines.extend(new_endpoint.split('\n'))
            new_lines.extend(['\n'])
            
            # Agregar el resto del archivo si hay más contenido
            if end_line < len(lines):
                new_lines.extend(lines[end_line:])
            
            # Escribir el archivo corregido
            with open('app/routers/menu_restructured.py', 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print("✅ Router corregido exitosamente!")
            return True
        else:
            print("❌ No se encontró el problema en el archivo")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la corrección: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Script de Corrección Simple del Router")
    print("=" * 50)
    
    success = fix_router()
    
    if success:
        print("\n✅ Script ejecutado exitosamente!")
        print("   El router ha sido corregido.")
        print("   Ahora puedes reiniciar el servidor.")
    else:
        print("\n❌ Error durante la ejecución del script.")
        sys.exit(1)









