#!/usr/bin/env python3
"""
Script para arreglar el router directamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_router_direct():
    """Arreglar el router directamente"""
    try:
        print("🔧 Arreglando router directamente...")
        
        # Leer el archivo original
        with open('app/routers/menu_restructured.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Encontrar y eliminar todo el endpoint problemático
        import re
        
        # Patrón para encontrar el endpoint from-carta completo
        pattern = r'@router\.post\("/menus/from-carta/"\)\s*def create_menu_from_carta\([^}]+}'
        
        # Reemplazar con un endpoint simple y funcional
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
    """Crear nuevo menú del día desde Carta Restaurante"""
    try:
        from datetime import datetime
        
        # Crear el menú
        nuevo_menu = MenuDiaRestructured(
            fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            estado='ACTIVE'
        )
        db.add(nuevo_menu)
        db.commit()
        db.refresh(nuevo_menu)
        
        # Crear opciones desde Carta Restaurante
        opciones_creadas = []
        
        # Procesar platos fijos
        if platos_fijos_ids:
            platos_fijos_list = [int(id.strip()) for id in platos_fijos_ids.split(',') if id.strip()]
            for producto_id in platos_fijos_list:
                plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == producto_id).first()
                if plato:
                    # Crear opción si no existe
                    opcion_existente = db.query(OpcionPlato).filter(
                        OpcionPlato.nombre == plato.nombre,
                        OpcionPlato.tipo == 'Fijo'
                    ).first()
                    
                    if not opcion_existente:
                        nueva_opcion = OpcionPlato(
                            nombre=plato.nombre,
                            descripcion=plato.descripcion,
                            tipo='Fijo',
                            precio=plato.precio_base,
                            activo=True
                        )
                        db.add(nueva_opcion)
                        db.commit()
                        db.refresh(nueva_opcion)
                        opciones_creadas.append(nueva_opcion.id)
                    else:
                        opciones_creadas.append(opcion_existente.id)
        
        # Procesar platos variables
        if platos_variables_ids:
            platos_variables_list = [int(id.strip()) for id in platos_variables_ids.split(',') if id.strip()]
            for producto_id in platos_variables_list:
                plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == producto_id).first()
                if plato:
                    # Crear opción si no existe
                    opcion_existente = db.query(OpcionPlato).filter(
                        OpcionPlato.nombre == plato.nombre,
                        OpcionPlato.tipo == 'Variable'
                    ).first()
                    
                    if not opcion_existente:
                        nueva_opcion = OpcionPlato(
                            nombre=plato.nombre,
                            descripcion=plato.descripcion,
                            tipo='Variable',
                            precio=plato.precio_base,
                            activo=True
                        )
                        db.add(nueva_opcion)
                        db.commit()
                        db.refresh(nueva_opcion)
                        opciones_creadas.append(nueva_opcion.id)
                    else:
                        opciones_creadas.append(opcion_existente.id)
        
        # Agregar opciones al menú
        for opcion_id in opciones_creadas:
            menu_opcion = MenuDiaOpcion(
                menu_dia_id=nuevo_menu.id,
                opcion_id=opcion_id,
                disponible=True
            )
            db.add(menu_opcion)
        db.commit()
        
        return {
            "success": True,
            "message": "Menú creado exitosamente desde Carta Restaurante",
            "menu": {
                "id": nuevo_menu.id,
                "fecha": str(nuevo_menu.fecha),
                "nombre": nuevo_menu.nombre,
                "precio": float(nuevo_menu.precio),
                "estado": nuevo_menu.estado
            },
            "opciones_agregadas": len(opciones_creadas)
        }
    except Exception as e:
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
        
        print("✅ Router corregido exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la corrección: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Script de Corrección Directa del Router")
    print("=" * 50)
    
    success = fix_router_direct()
    
    if success:
        print("\n✅ Script ejecutado exitosamente!")
        print("   El router ha sido corregido.")
        print("   Ahora puedes reiniciar el servidor.")
    else:
        print("\n❌ Error durante la ejecución del script.")
        sys.exit(1)







