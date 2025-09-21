"""
Router simplificado para probar el sistema de menús reestructurado
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.menu_restructured import (
    CategoriaPlatoVariable, 
    OpcionPlato, 
    MenuDiaRestructured, 
    MenuDiaOpcion
)

router = APIRouter(prefix="/menu-restructured", tags=["menu-restructured"])

# ============================================================================
# ENDPOINTS SIMPLIFICADOS PARA PRUEBAS
# ============================================================================

@router.get("/categorias/")
def get_categorias_simple(db: Session = Depends(get_db)):
    """Obtener categorías de forma simple"""
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
                    "activo": cat.activo
                }
                for cat in categorias
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "categorias": []
        }

@router.get("/opciones/")
def get_opciones_simple(db: Session = Depends(get_db)):
    """Obtener opciones de forma simple"""
    try:
        opciones = db.query(OpcionPlato).all()
        return {
            "success": True,
            "total": len(opciones),
            "opciones": [
                {
                    "id": op.id,
                    "nombre": op.nombre,
                    "tipo": op.tipo,
                    "precio": float(op.precio),
                    "activo": op.activo,
                    "categoria": op.categoria.nombre if op.categoria else None
                }
                for op in opciones
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "opciones": []
        }

@router.get("/menus/")
def get_menus_simple(db: Session = Depends(get_db)):
    """Obtener menús de forma simple"""
    try:
        menus = db.query(MenuDiaRestructured).all()
        return {
            "success": True,
            "total": len(menus),
            "menus": [
                {
                    "id": menu.id,
                    "fecha": str(menu.fecha),
                    "nombre": menu.nombre,
                    "precio": float(menu.precio),
                    "estado": menu.estado
                }
                for menu in menus
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "menus": []
        }

@router.get("/stats/")
def get_stats_simple(db: Session = Depends(get_db)):
    """Obtener estadísticas del sistema"""
    try:
        categorias_count = db.query(CategoriaPlatoVariable).count()
        opciones_count = db.query(OpcionPlato).count()
        menus_count = db.query(MenuDiaRestructured).count()
        
        platos_fijos = db.query(OpcionPlato).filter(OpcionPlato.tipo == 'Fijo').count()
        platos_variables = db.query(OpcionPlato).filter(OpcionPlato.tipo == 'Variable').count()
        
        return {
            "success": True,
            "stats": {
                "categorias": categorias_count,
                "opciones": opciones_count,
                "menus": menus_count,
                "platos_fijos": platos_fijos,
                "platos_variables": platos_variables
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stats": {}
        }

@router.post("/opciones/")
def create_opcion_simple(
    nombre: str,
    descripcion: str = "",
    tipo: str = "Variable",
    categoria_id: int = None,
    precio: float = 0.0,
    activo: bool = True,
    db: Session = Depends(get_db)
):
    """Crear nueva opción de plato"""
    try:
        nueva_opcion = OpcionPlato(
            nombre=nombre,
            descripcion=descripcion,
            tipo=tipo,
            categoria_id=categoria_id,
            precio=precio,
            activo=activo
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
                "tipo": nueva_opcion.tipo,
                "precio": float(nueva_opcion.precio),
                "activo": nueva_opcion.activo
            }
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Error al crear la opción"
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
        
        # Verificar que no exista menú para la misma fecha
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        existing = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.fecha == fecha_obj).first()
        if existing:
            return {
                "success": False,
                "message": f"Ya existe un menú para la fecha {fecha}"
            }
        
        # Crear el menú
        nuevo_menu = MenuDiaRestructured(
            fecha=fecha_obj,
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

@router.get("/menus/")
def get_menus(
    fecha: str = None,
    activo: bool = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de menús del día"""
    try:
        query = db.query(MenuDiaRestructured)
        
        if fecha:
            from datetime import datetime
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            query = query.filter(MenuDiaRestructured.fecha == fecha_obj)
        
        if activo is not None:
            estado = 'ACTIVE' if activo else 'INACTIVE'
            query = query.filter(MenuDiaRestructured.estado == estado)
        
        menus = query.order_by(MenuDiaRestructured.fecha.desc()).all()
        
        menus_data = []
        for menu in menus:
            # Obtener opciones del menú
            opciones = db.query(MenuDiaOpcion).filter(MenuDiaOpcion.menu_dia_id == menu.id).all()
            opciones_data = []
            for opcion in opciones:
                opcion_info = db.query(OpcionPlato).filter(OpcionPlato.id == opcion.opcion_id).first()
                if opcion_info:
                    opciones_data.append({
                        "id": opcion_info.id,
                        "nombre": opcion_info.nombre,
                        "precio": float(opcion_info.precio),
                        "tipo": opcion_info.tipo,
                        "disponible": opcion.disponible
                    })
            
            menus_data.append({
                "id": menu.id,
                "fecha": str(menu.fecha),
                "nombre": menu.nombre,
                "descripcion": menu.descripcion,
                "precio": float(menu.precio),
                "estado": menu.estado,
                "opciones": opciones_data,
                "created_at": menu.created_at.isoformat() if menu.created_at else None
            })
        
        return {
            "success": True,
            "menus": menus_data,
            "total": len(menus_data)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al obtener menús"
        }

@router.get("/menus/{menu_id}")
def get_menu(menu_id: int, db: Session = Depends(get_db)):
    """Obtener menú específico por ID"""
    try:
        menu = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.id == menu_id).first()
        if not menu:
            return {
                "success": False,
                "message": "Menú no encontrado"
            }
        
        # Obtener opciones del menú
        opciones = db.query(MenuDiaOpcion).filter(MenuDiaOpcion.menu_dia_id == menu.id).all()
        opciones_data = []
        for opcion in opciones:
            opcion_info = db.query(OpcionPlato).filter(OpcionPlato.id == opcion.opcion_id).first()
            if opcion_info:
                opciones_data.append({
                    "id": opcion_info.id,
                    "nombre": opcion_info.nombre,
                    "precio": float(opcion_info.precio),
                    "tipo": opcion_info.tipo,
                    "disponible": opcion.disponible
                })
        
        return {
            "success": True,
            "menu": {
                "id": menu.id,
                "fecha": str(menu.fecha),
                "nombre": menu.nombre,
                "descripcion": menu.descripcion,
                "precio": float(menu.precio),
                "estado": menu.estado,
                "opciones": opciones_data,
                "created_at": menu.created_at.isoformat() if menu.created_at else None
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al obtener menú"
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
    db: Session = Depends(get_db)
):
    """Actualizar menú existente"""
    try:
        menu = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.id == menu_id).first()
        if not menu:
            return {
                "success": False,
                "message": "Menú no encontrado"
            }
        
        # Actualizar campos si se proporcionan
        if fecha:
            from datetime import datetime
            menu.fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        if nombre:
            menu.nombre = nombre
        if descripcion is not None:
            menu.descripcion = descripcion
        if precio is not None:
            menu.precio = precio
        if estado:
            menu.estado = estado
        
        # Actualizar opciones si se proporcionan
        if opciones_ids is not None:
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
        db.refresh(menu)
        
        return {
            "success": True,
            "message": "Menú actualizado exitosamente",
            "menu": {
                "id": menu.id,
                "fecha": str(menu.fecha),
                "nombre": menu.nombre,
                "precio": float(menu.precio),
                "estado": menu.estado
            }
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Error al actualizar menú"
        }

@router.post("/menus/{menu_id}/duplicate")
def duplicate_menu(menu_id: int, nueva_fecha: str, db: Session = Depends(get_db)):
    """Duplicar menú existente a una nueva fecha"""
    try:
        from datetime import datetime
        
        # Obtener menú original
        menu_original = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.id == menu_id).first()
        if not menu_original:
            return {
                "success": False,
                "message": "Menú original no encontrado"
            }
        
        # Verificar que no exista menú para la nueva fecha
        nueva_fecha_obj = datetime.strptime(nueva_fecha, '%Y-%m-%d').date()
        existing = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.fecha == nueva_fecha_obj).first()
        if existing:
            return {
                "success": False,
                "message": f"Ya existe un menú para la fecha {nueva_fecha}"
            }
        
        # Crear nuevo menú
        nuevo_menu = MenuDiaRestructured(
            fecha=nueva_fecha_obj,
            nombre=f"{menu_original.nombre} (Copia)",
            descripcion=menu_original.descripcion,
            precio=menu_original.precio,
            estado='ACTIVE'
        )
        db.add(nuevo_menu)
        db.commit()
        db.refresh(nuevo_menu)
        
        # Copiar opciones del menú original
        opciones_originales = db.query(MenuDiaOpcion).filter(MenuDiaOpcion.menu_dia_id == menu_id).all()
        for opcion in opciones_originales:
            nueva_opcion = MenuDiaOpcion(
                menu_dia_id=nuevo_menu.id,
                opcion_id=opcion.opcion_id,
                disponible=opcion.disponible
            )
            db.add(nueva_opcion)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Menú duplicado exitosamente",
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
            "message": "Error al duplicar menú"
        }

@router.delete("/menus/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    """Eliminar menú del día"""
    try:
        menu = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.id == menu_id).first()
        if not menu:
            return {
                "success": False,
                "message": "Menú no encontrado"
            }
        
        # Eliminar opciones asociadas
        db.query(MenuDiaOpcion).filter(MenuDiaOpcion.menu_dia_id == menu_id).delete()
        
        # Eliminar menú
        db.delete(menu)
        db.commit()
        
        return {
            "success": True,
            "message": "Menú eliminado exitosamente"
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Error al eliminar menú"
        }

@router.put("/menus/{menu_id}/toggle-status")
def toggle_menu_status(menu_id: int, db: Session = Depends(get_db)):
    """Activar/desactivar menú"""
    try:
        menu = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.id == menu_id).first()
        if not menu:
            return {
                "success": False,
                "message": "Menú no encontrado"
            }
        
        # Cambiar estado
        nuevo_estado = 'INACTIVE' if menu.estado == 'ACTIVE' else 'ACTIVE'
        menu.estado = nuevo_estado
        db.commit()
        
        return {
            "success": True,
            "message": f"Menú {'activado' if nuevo_estado == 'ACTIVE' else 'desactivado'} exitosamente",
            "estado": nuevo_estado
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Error al cambiar estado del menú"
        }
