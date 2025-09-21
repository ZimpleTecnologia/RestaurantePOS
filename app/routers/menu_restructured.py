"""
Router simplificado para probar el sistema de menús reestructurado
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import os
import shutil
import time
from app.database import get_db
from app.models.menu_restructured import MenuDiaRestructured, OpcionPlato, MenuDiaOpcion, CategoriaPlatoVariable
from app.models.carta_restaurante import CartaRestaurante

router = APIRouter()

@router.get("/")
def get_menu_restructured_home():
    """Página principal del sistema de menús reestructurado"""
    return {"message": "Sistema de Menús Reestructurado", "version": "1.0"}

@router.get("/stats/")
def get_menu_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas del sistema de menús"""
    try:
        total_menus = db.query(MenuDiaRestructured).count()
        total_opciones = db.query(OpcionPlato).count()
        total_categorias = db.query(CategoriaPlatoVariable).count()
        
        return {
            "success": True,
            "stats": {
                "total_menus": total_menus,
                "total_opciones": total_opciones,
                "total_categorias": total_categorias
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/menus/")
def get_menus(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de menús del día"""
    try:
        menus = db.query(MenuDiaRestructured).offset(skip).limit(limit).all()
        return {
            "success": True,
            "total": len(menus),
            "menus": [
                {
                    "id": menu.id,
                    "fecha": str(menu.fecha),
                    "nombre": menu.nombre,
                    "precio": float(menu.precio),
                    "estado": menu.estado,
                    "descripcion": menu.descripcion
                }
                for menu in menus
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/menus/{menu_id}")
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    """Obtener un menú específico"""
    try:
        menu = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.id == menu_id).first()
        if not menu:
            raise HTTPException(status_code=404, detail="Menú no encontrado")
        
        return {
            "success": True,
            "menu": {
                "id": menu.id,
                "fecha": str(menu.fecha),
                "nombre": menu.nombre,
                "precio": float(menu.precio),
                "estado": menu.estado,
                "descripcion": menu.descripcion
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categorias/")
def get_categorias(db: Session = Depends(get_db)):
    """Obtener categorías de platos variables"""
    try:
        categorias = db.query(CategoriaPlatoVariable).all()
        return {
            "success": True,
            "total": len(categorias),
            "categorias": [
                {
                    "id": cat.id,
                    "nombre": cat.nombre,
                    "descripcion": cat.descripcion,
                    "activa": cat.activa
                }
                for cat in categorias
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/opciones/")
def get_opciones(db: Session = Depends(get_db)):
    """Obtener opciones de platos"""
    try:
        opciones = db.query(OpcionPlato).all()
        print(f"🔍 Cargando {len(opciones)} opciones...")
        
        opciones_data = []
        for opcion in opciones:
            tiene_imagen = opcion.imagen_data is not None
            print(f"   📊 {opcion.nombre}: tiene_imagen={tiene_imagen}, imagen_data_size={len(opcion.imagen_data) if opcion.imagen_data else 0}")
            
            opciones_data.append({
                "id": opcion.id,
                "nombre": opcion.nombre,
                "descripcion": opcion.descripcion,
                "tipo": opcion.tipo,
                "precio": float(opcion.precio),
                "activo": opcion.activo,
                "imagen_data": tiene_imagen,
                "tiene_imagen": tiene_imagen
            })
        
        return {
            "success": True,
            "total": len(opciones),
            "opciones": opciones_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/platos-fijos/")
def get_platos_fijos(db: Session = Depends(get_db)):
    """Obtener platos fijos desde Carta Restaurante"""
    try:
        platos_fijos = db.query(CartaRestaurante).filter(
            CartaRestaurante.tipo == 'Fijo',
            CartaRestaurante.activo == True
        ).all()
        return {
            "success": True,
            "total": len(platos_fijos),
            "platos": [
                {
                    "producto_id": plato.producto_id,
                    "nombre": plato.nombre,
                    "descripcion": plato.descripcion,
                    "precio_base": float(plato.precio_base),
                    "tipo": plato.tipo,
                    "categoria": plato.categoria,
                    "activo": plato.activo
                }
                for plato in platos_fijos
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "platos": []
        }

@router.get("/platos-variables/")
def get_platos_variables(db: Session = Depends(get_db)):
    """Obtener platos variables desde Carta Restaurante"""
    try:
        platos_variables = db.query(CartaRestaurante).filter(
            CartaRestaurante.tipo == 'Variable',
            CartaRestaurante.activo == True
        ).all()
        return {
            "success": True,
            "total": len(platos_variables),
            "platos": [
                {
                    "producto_id": plato.producto_id,
                    "nombre": plato.nombre,
                    "descripcion": plato.descripcion,
                    "precio_base": float(plato.precio_base),
                    "tipo": plato.tipo,
                    "categoria": plato.categoria,
                    "activo": plato.activo
                }
                for plato in platos_variables
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "platos": []
        }

@router.post("/menus/")
def create_menu_simple(
    fecha: str,
    nombre: str,
    descripcion: str = "",
    precio: float = 0.0,
    opciones_ids: str = "",
    db: Session = Depends(get_db)
):
    """Crear nuevo menú del día"""
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
        
        # Agregar opciones si se proporcionan
        if opciones_ids:
            opciones_list = [int(id.strip()) for id in opciones_ids.split(',') if id.strip()]
            for opcion_id in opciones_list:
                menu_opcion = MenuDiaOpcion(
                    menu_dia_id=nuevo_menu.id,
                    opcion_id=opcion_id,
                    disponible=True
                )
                db.add(menu_opcion)
            db.commit()
        
        return {
            "success": True,
            "message": "Menú creado exitosamente",
            "menu": {
                "id": nuevo_menu.id,
                "fecha": str(nuevo_menu.fecha),
                "nombre": nuevo_menu.nombre,
                "precio": float(nuevo_menu.precio),
                "estado": nuevo_menu.estado
            }
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Error al crear el menú"
        }

@router.post("/menus/from-carta/")
def create_menu_from_carta(
    fecha: str,
    nombre: str,
    descripcion: str = "",
    precio: float = 0.0,
    platos_fijos_ids: str = "",
    platos_variables_ids: str = "",
    db: Session = Depends(get_db)
):
    """Crear nuevo menú del día desde Carta Restaurante usando SQL directo"""
    try:
        from datetime import datetime
        
        print(f"🔍 Creando menú con opciones de platos:")
        print(f"   Fecha: {fecha}")
        print(f"   Nombre: {nombre}")
        print(f"   Precio: {precio}")
        print(f"   Platos fijos IDs: {platos_fijos_ids}")
        print(f"   Platos variables IDs: {platos_variables_ids}")
        
        # Verificar si ya existe un menú para esta fecha
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        menu_existente = db.execute(text("""
            SELECT id, nombre FROM menus_dia WHERE fecha = :fecha
        """), {"fecha": fecha_obj}).fetchone()
        
        if menu_existente:
            print(f"⚠️ Ya existe un menú para la fecha {fecha}: '{menu_existente.nombre}' (ID: {menu_existente.id})")
            return {
                "success": False,
                "error": f"Ya existe un menú para la fecha {fecha}",
                "message": f"Ya existe un menú llamado '{menu_existente.nombre}' para la fecha {fecha}. Por favor, elige una fecha diferente o edita el menú existente."
            }
        
        # Crear el menú usando consulta SQL directa
        result = db.execute(text("""
            INSERT INTO menus_dia (fecha, nombre, descripcion, precio, estado)
            VALUES (:fecha, :nombre, :descripcion, :precio, 'ACTIVE')
            RETURNING id
        """), {
            "fecha": fecha_obj,
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
                plato_data = db.execute(text("""
                    SELECT nombre, descripcion, precio_base, tipo
                    FROM carta_restaurante
                    WHERE producto_id = :producto_id AND activo = true
                """), {"producto_id": producto_id}).fetchone()
                
                if plato_data:
                    # Buscar opción existente
                    opcion_id = db.execute(text("""
                        SELECT id FROM opciones_platos
                        WHERE nombre = :nombre AND tipo = 'Fijo'
                    """), {"nombre": plato_data.nombre}).scalar()
                    
                    if not opcion_id:
                        # Crear nueva opción
                        new_opcion_result = db.execute(text("""
                            INSERT INTO opciones_platos (nombre, descripcion, tipo, precio, activo)
                            VALUES (:nombre, :descripcion, 'Fijo', :precio, true)
                            RETURNING id
                        """), {
                            "nombre": plato_data.nombre,
                            "descripcion": plato_data.descripcion,
                            "precio": float(plato_data.precio_base)
                        })
                        opcion_id = new_opcion_result.scalar()
                        print(f"   ✅ Nueva opción creada: {plato_data.nombre} (ID: {opcion_id})")
                    else:
                        print(f"   ✅ Opción existente encontrada: {plato_data.nombre} (ID: {opcion_id})")
                    opciones_creadas.append(opcion_id)
        
        # Procesar platos variables
        if platos_variables_ids:
            platos_variables_list = [int(id.strip()) for id in platos_variables_ids.split(',') if id.strip()]
            print(f"🔄 Procesando {len(platos_variables_list)} platos variables: {platos_variables_list}")
            for producto_id in platos_variables_list:
                plato_data = db.execute(text("""
                    SELECT nombre, descripcion, precio_base, tipo
                    FROM carta_restaurante
                    WHERE producto_id = :producto_id AND activo = true
                """), {"producto_id": producto_id}).fetchone()
                
                if plato_data:
                    # Buscar opción existente
                    opcion_id = db.execute(text("""
                        SELECT id FROM opciones_platos
                        WHERE nombre = :nombre AND tipo = 'Variable'
                    """), {"nombre": plato_data.nombre}).scalar()
                    
                    if not opcion_id:
                        # Crear nueva opción
                        new_opcion_result = db.execute(text("""
                            INSERT INTO opciones_platos (nombre, descripcion, tipo, precio, activo)
                            VALUES (:nombre, :descripcion, 'Variable', :precio, true)
                            RETURNING id
                        """), {
                            "nombre": plato_data.nombre,
                            "descripcion": plato_data.descripcion,
                            "precio": float(plato_data.precio_base)
                        })
                        opcion_id = new_opcion_result.scalar()
                        print(f"   ✅ Nueva opción creada: {plato_data.nombre} (ID: {opcion_id})")
                    else:
                        print(f"   ✅ Opción existente encontrada: {plato_data.nombre} (ID: {opcion_id})")
                    opciones_creadas.append(opcion_id)
        
        # Agregar opciones al menú
        print(f"📋 Agregando {len(opciones_creadas)} opciones al menú")
        for opcion_id in opciones_creadas:
            db.execute(text("""
                INSERT INTO menu_dia_opciones (menu_dia_id, opcion_id, disponible)
                VALUES (:menu_dia_id, :opcion_id, true)
            """), {"menu_dia_id": menu_id, "opcion_id": opcion_id})
        db.commit()
        
        print(f"✅ Menú creado exitosamente con {len(opciones_creadas)} opciones")
        return {
            "success": True,
            "message": "Menú creado exitosamente desde Carta Restaurante",
            "menu": {
                "id": menu_id,
                "fecha": str(datetime.strptime(fecha, '%Y-%m-%d').date()),
                "nombre": nombre,
                "precio": float(precio),
                "estado": 'ACTIVE'
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
        }

@router.put("/menus/{menu_id}")
def update_menu(
    menu_id: int,
    fecha: str = None,
    nombre: str = None,
    descripcion: str = None,
    precio: float = None,
    estado: str = None,
    opciones_ids: str = None,
    platos_fijos_ids: str = None,
    platos_variables_ids: str = None,
    db: Session = Depends(get_db)
):
    """Actualizar menú del día"""
    try:
        from datetime import datetime
        
        print(f"🔄 Actualizando menú ID: {menu_id}")
        print(f"   Fecha: {fecha}")
        print(f"   Nombre: {nombre}")
        print(f"   Platos fijos IDs: {platos_fijos_ids}")
        print(f"   Platos variables IDs: {platos_variables_ids}")
        
        # Verificar que el menú existe usando consulta SQL directa
        menu_existente = db.execute(text("""
            SELECT id, nombre, fecha FROM menus_dia WHERE id = :menu_id
        """), {"menu_id": menu_id}).fetchone()
        
        if not menu_existente:
            raise HTTPException(status_code=404, detail="Menú no encontrado")
        
        print(f"✅ Menú encontrado: {menu_existente.nombre} (ID: {menu_existente.id})")
        
        # Actualizar campos usando consulta SQL directa
        update_fields = []
        update_values = {"menu_id": menu_id}
        
        if fecha:
            update_fields.append("fecha = :fecha")
            update_values["fecha"] = datetime.strptime(fecha, '%Y-%m-%d').date()
        if nombre:
            update_fields.append("nombre = :nombre")
            update_values["nombre"] = nombre
        if descripcion is not None:
            update_fields.append("descripcion = :descripcion")
            update_values["descripcion"] = descripcion
        if precio is not None:
            update_fields.append("precio = :precio")
            update_values["precio"] = precio
        if estado:
            update_fields.append("estado = :estado")
            update_values["estado"] = estado
        
        if update_fields:
            update_fields.append("updated_at = NOW()")
            update_query = f"""
                UPDATE menus_dia 
                SET {', '.join(update_fields)}
                WHERE id = :menu_id
            """
            db.execute(text(update_query), update_values)
            db.commit()
            print(f"✅ Campos del menú actualizados: {', '.join([f.split(' = ')[0] for f in update_fields[:-1]])}")
        
        # Si se proporcionan platos fijos y variables, procesarlos como en la creación
        if platos_fijos_ids or platos_variables_ids:
            print(f"🍽️ Procesando platos para actualización del menú")
            
            # Eliminar opciones existentes del menú
            db.execute(text("""
                DELETE FROM menu_dia_opciones WHERE menu_dia_id = :menu_id
            """), {"menu_id": menu_id})
            
            opciones_creadas = []
            
            # Procesar platos fijos
            if platos_fijos_ids:
                platos_fijos_list = [int(id.strip()) for id in platos_fijos_ids.split(',') if id.strip()]
                print(f"🍽️ Procesando {len(platos_fijos_list)} platos fijos: {platos_fijos_list}")
                for producto_id in platos_fijos_list:
                    plato_data = db.execute(text("""
                        SELECT nombre, descripcion, precio_base, tipo
                        FROM carta_restaurante
                        WHERE producto_id = :producto_id AND activo = true
                    """), {"producto_id": producto_id}).fetchone()
                    
                    if plato_data:
                        # Buscar opción existente
                        opcion_id = db.execute(text("""
                            SELECT id FROM opciones_platos
                            WHERE nombre = :nombre AND tipo = 'Fijo'
                        """), {"nombre": plato_data.nombre}).scalar()
                        
                        if not opcion_id:
                            # Crear nueva opción
                            new_opcion_result = db.execute(text("""
                                INSERT INTO opciones_platos (nombre, descripcion, tipo, precio, activo)
                                VALUES (:nombre, :descripcion, 'Fijo', :precio, true)
                                RETURNING id
                            """), {
                                "nombre": plato_data.nombre,
                                "descripcion": plato_data.descripcion,
                                "precio": float(plato_data.precio_base)
                            })
                            opcion_id = new_opcion_result.scalar()
                            print(f"   ✅ Nueva opción creada: {plato_data.nombre} (ID: {opcion_id})")
                        else:
                            print(f"   ✅ Opción existente encontrada: {plato_data.nombre} (ID: {opcion_id})")
                        opciones_creadas.append(opcion_id)
            
            # Procesar platos variables
            if platos_variables_ids:
                platos_variables_list = [int(id.strip()) for id in platos_variables_ids.split(',') if id.strip()]
                print(f"🔄 Procesando {len(platos_variables_list)} platos variables: {platos_variables_list}")
                for producto_id in platos_variables_list:
                    plato_data = db.execute(text("""
                        SELECT nombre, descripcion, precio_base, tipo
                        FROM carta_restaurante
                        WHERE producto_id = :producto_id AND activo = true
                    """), {"producto_id": producto_id}).fetchone()
                    
                    if plato_data:
                        # Buscar opción existente
                        opcion_id = db.execute(text("""
                            SELECT id FROM opciones_platos
                            WHERE nombre = :nombre AND tipo = 'Variable'
                        """), {"nombre": plato_data.nombre}).scalar()
                        
                        if not opcion_id:
                            # Crear nueva opción
                            new_opcion_result = db.execute(text("""
                                INSERT INTO opciones_platos (nombre, descripcion, tipo, precio, activo)
                                VALUES (:nombre, :descripcion, 'Variable', :precio, true)
                                RETURNING id
                            """), {
                                "nombre": plato_data.nombre,
                                "descripcion": plato_data.descripcion,
                                "precio": float(plato_data.precio_base)
                            })
                            opcion_id = new_opcion_result.scalar()
                            print(f"   ✅ Nueva opción creada: {plato_data.nombre} (ID: {opcion_id})")
                        else:
                            print(f"   ✅ Opción existente encontrada: {plato_data.nombre} (ID: {opcion_id})")
                        opciones_creadas.append(opcion_id)
            
            # Agregar opciones al menú
            print(f"📋 Agregando {len(opciones_creadas)} opciones al menú")
            for opcion_id in opciones_creadas:
                db.execute(text("""
                    INSERT INTO menu_dia_opciones (menu_dia_id, opcion_id, disponible)
                    VALUES (:menu_dia_id, :opcion_id, true)
                """), {"menu_dia_id": menu_id, "opcion_id": opcion_id})
            
            db.commit()
            print(f"✅ Menú actualizado con {len(opciones_creadas)} opciones")
        
        # Manejar opciones_ids si se proporciona (método anterior)
        elif opciones_ids is not None:
            # Eliminar opciones existentes
            db.query(MenuDiaOpcion).filter(MenuDiaOpcion.menu_dia_id == menu_id).delete()
            
            # Agregar nuevas opciones
            if opciones_ids:
                opciones_list = [int(id.strip()) for id in opciones_ids.split(',') if id.strip()]
                for opcion_id in opciones_list:
                    menu_opcion = MenuDiaOpcion(
                        menu_dia_id=menu_id,
                        opcion_id=opcion_id,
                        disponible=True
                    )
                    db.add(menu_opcion)
            db.commit()
        
        # Obtener información actualizada del menú
        menu_actualizado = db.execute(text("""
            SELECT id, fecha, nombre, descripcion, precio, estado
            FROM menus_dia WHERE id = :menu_id
        """), {"menu_id": menu_id}).fetchone()
        
        return {
            "success": True,
            "message": "Menú actualizado exitosamente",
            "menu": {
                "id": menu_actualizado.id,
                "fecha": str(menu_actualizado.fecha),
                "nombre": menu_actualizado.nombre,
                "descripcion": menu_actualizado.descripcion,
                "precio": float(menu_actualizado.precio),
                "estado": menu_actualizado.estado
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al actualizar menú: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/menus/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    """Eliminar menú del día"""
    try:
        menu = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.id == menu_id).first()
        if not menu:
            raise HTTPException(status_code=404, detail="Menú no encontrado")
        
        # Eliminar opciones asociadas
        db.query(MenuDiaOpcion).filter(MenuDiaOpcion.menu_dia_id == menu_id).delete()
        
        # Eliminar menú
        db.delete(menu)
        db.commit()
        
        return {
            "success": True,
            "message": "Menú eliminado exitosamente"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/opciones/with-image/")
def create_opcion_with_image(
    nombre: str = Form(...),
    descripcion: str = Form(""),
    tipo: str = Form(...),
    precio: float = Form(...),
    categoria_id: int = Form(None),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Crear nueva opción de plato con imagen (almacenada en BD)"""
    try:
        # Procesar imagen si se proporciona
        imagen_data = None
        imagen_tipo = None
        
        if imagen and imagen.filename:
            try:
                # Leer contenido de la imagen
                imagen_data = imagen.file.read()
                imagen_tipo = imagen.content_type
            except Exception as e:
                print(f"Error al procesar imagen: {str(e)}")
                # Continuar sin imagen si hay error
        
        # Crear la opción
        nueva_opcion = OpcionPlato(
            nombre=nombre,
            descripcion=descripcion,
            tipo=tipo,
            precio=precio,
            categoria_id=categoria_id,
            imagen_data=imagen_data,
            imagen_tipo=imagen_tipo,
            activo=True
        )
        db.add(nueva_opcion)
        db.commit()
        db.refresh(nueva_opcion)
        
        return {
            "success": True,
            "message": "Opción creada exitosamente",
            "opcion": {
                "id": nueva_opcion.id,
                "nombre": nueva_opcion.nombre,
                "descripcion": nueva_opcion.descripcion,
                "tipo": nueva_opcion.tipo,
                "precio": float(nueva_opcion.precio),
                "tiene_imagen": nueva_opcion.imagen_data is not None
            }
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Error al crear la opción"
        }

@router.put("/opciones/{opcion_id}/with-image/")
def update_opcion_with_image(
    opcion_id: int,
    nombre: str = Form(None),
    descripcion: str = Form(None),
    tipo: str = Form(None),
    precio: float = Form(None),
    categoria_id: int = Form(None),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Actualizar opción de plato con imagen (almacenada en BD)"""
    try:
        opcion = db.query(OpcionPlato).filter(OpcionPlato.id == opcion_id).first()
        if not opcion:
            raise HTTPException(status_code=404, detail="Opción no encontrada")
        
        # Actualizar campos si se proporcionan
        if nombre is not None:
            opcion.nombre = nombre
        if descripcion is not None:
            opcion.descripcion = descripcion
        if tipo is not None:
            opcion.tipo = tipo
        if precio is not None:
            opcion.precio = precio
        if categoria_id is not None:
            opcion.categoria_id = categoria_id
        
        # Procesar imagen si se proporciona
        if imagen and imagen.filename:
            try:
                # Leer contenido de la imagen
                imagen_data = imagen.file.read()
                imagen_tipo = imagen.content_type
                
                # Actualizar la opción con la nueva imagen
                opcion.imagen_data = imagen_data
                opcion.imagen_tipo = imagen_tipo
                
            except Exception as e:
                print(f"Error al procesar imagen: {str(e)}")
                # Continuar sin actualizar imagen si hay error
        
        db.commit()
        db.refresh(opcion)
        
        return {
            "success": True,
            "message": "Opción actualizada exitosamente",
            "opcion": {
                "id": opcion.id,
                "nombre": opcion.nombre,
                "descripcion": opcion.descripcion,
                "tipo": opcion.tipo,
                "precio": float(opcion.precio),
                "tiene_imagen": opcion.imagen_data is not None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Error al actualizar la opción"
        }

@router.get("/opciones/{opcion_id}/imagen")
def get_opcion_image(opcion_id: int, db: Session = Depends(get_db)):
    """Obtener imagen de una opción (desde BD)"""
    try:
        print(f"🔍 Buscando imagen para opción ID: {opcion_id}")
        opcion = db.query(OpcionPlato).filter(OpcionPlato.id == opcion_id).first()
        
        if not opcion:
            print(f"❌ Opción {opcion_id} no encontrada")
            raise HTTPException(status_code=404, detail="Opción no encontrada")
        
        if not opcion.imagen_data:
            print(f"❌ Opción {opcion_id} no tiene imagen_data")
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        
        print(f"✅ Imagen encontrada para opción {opcion_id}, tamaño: {len(opcion.imagen_data)} bytes")
        print(f"📊 Tipo de imagen: {opcion.imagen_tipo}")
        
        # Devolver imagen desde la base de datos
        return Response(
            content=opcion.imagen_data, 
            media_type=opcion.imagen_tipo or 'image/jpeg'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Error al obtener imagen: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
