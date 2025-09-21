#!/usr/bin/env python3
"""
Script para restaurar el router menu_restructured.py completamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def restore_router():
    """Restaurar el router completamente"""
    try:
        print("🔧 Restaurando router menu_restructured.py...")
        
        # Crear el router completo desde cero
        router_content = '''"""
Router simplificado para probar el sistema de menús reestructurado
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
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
        return {
            "success": True,
            "total": len(opciones),
            "opciones": [
                {
                    "id": opcion.id,
                    "nombre": opcion.nombre,
                    "descripcion": opcion.descripcion,
                    "tipo": opcion.tipo,
                    "precio": float(opcion.precio),
                    "activo": opcion.activo
                }
                for opcion in opciones
            ]
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
    """Actualizar menú del día"""
    try:
        menu = db.query(MenuDiaRestructured).filter(MenuDiaRestructured.id == menu_id).first()
        if not menu:
            raise HTTPException(status_code=404, detail="Menú no encontrado")
        
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
        
        db.commit()
        db.refresh(menu)
        
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
    except HTTPException:
        raise
    except Exception as e:
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
'''
        
        # Escribir el archivo completamente nuevo
        with open('app/routers/menu_restructured.py', 'w', encoding='utf-8') as f:
            f.write(router_content)
        
        print("✅ Router restaurado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la restauración: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Script de Restauración del Router")
    print("=" * 50)
    
    success = restore_router()
    
    if success:
        print("\n✅ Script ejecutado exitosamente!")
        print("   El router ha sido restaurado completamente.")
        print("   Ahora puedes reiniciar el servidor sin problemas.")
    else:
        print("\n❌ Error durante la ejecución del script.")
        sys.exit(1)
