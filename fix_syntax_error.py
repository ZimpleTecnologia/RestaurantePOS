#!/usr/bin/env python3
"""
Script para corregir el error de sintaxis en menu_restructured.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_syntax_error():
    """Corregir el error de sintaxis en el router"""
    try:
        print("🔧 Corrigiendo error de sintaxis en menu_restructured.py...")
        
        # Leer el archivo actual
        with open('app/routers/menu_restructured.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el endpoint problemático y reemplazarlo
        import re
        
        # Patrón para encontrar el endpoint from-carta problemático
        pattern = r'@router\.post\("/menus/from-carta/"\)\s*def create_menu_from_carta\([^}]+}'
        
        # Endpoint corregido
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
        
        # Crear opciones desde Carta Restaurante usando consultas SQL directas
        opciones_creadas = []
        
        # Procesar platos fijos
        if platos_fijos_ids:
            platos_fijos_list = [int(id.strip()) for id in platos_fijos_ids.split(',') if id.strip()]
            print(f"🍽️ Procesando {len(platos_fijos_list)} platos fijos: {platos_fijos_list}")
            
            for producto_id in platos_fijos_list:
                # Obtener datos del plato desde Carta Restaurante
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
                        print(f"   ✅ Opción existente: {plato[0]} (ID: {opcion_existente[0]})")
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
                        print(f"   ✅ Nueva opción creada: {plato[0]} (ID: {opcion_id})")
        
        # Procesar platos variables
        if platos_variables_ids:
            platos_variables_list = [int(id.strip()) for id in platos_variables_ids.split(',') if id.strip()]
            print(f"🔄 Procesando {len(platos_variables_list)} platos variables: {platos_variables_list}")
            
            for producto_id in platos_variables_list:
                # Obtener datos del plato desde Carta Restaurante
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
                        print(f"   ✅ Opción existente: {plato[0]} (ID: {opcion_existente[0]})")
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
                        print(f"   ✅ Nueva opción creada: {plato[0]} (ID: {opcion_id})")
        
        # Crear relaciones usando consultas SQL directas
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
        print(f"✅ {len(opciones_creadas)} relaciones creadas exitosamente")
        
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
        print(f"   Tipo de error: {type(e).__name__}")
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Error al crear el menú desde Carta Restaurante"
        }'''
        
        # Reemplazar el endpoint problemático
        new_content = re.sub(pattern, new_endpoint, content, flags=re.DOTALL)
        
        # Guardar el archivo corregido
        with open('app/routers/menu_restructured.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Error de sintaxis corregido exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la corrección: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Script de Corrección de Error de Sintaxis")
    print("=" * 50)
    
    success = fix_syntax_error()
    
    if success:
        print("\n✅ Script ejecutado exitosamente!")
        print("   El error de sintaxis ha sido corregido.")
        print("   Ahora puedes reiniciar el servidor.")
    else:
        print("\n❌ Error durante la ejecución del script.")
        sys.exit(1)









