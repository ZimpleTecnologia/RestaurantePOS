"""
Router público para probar el sistema de menús sin autenticación
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.menu_unified import Menu, Plato
from app.schemas.menu_unified import MenuResponse, PlatoResponse

router = APIRouter(prefix="/public/menus", tags=["menús públicos"])


@router.get("/platos/", response_model=List[PlatoResponse])
def get_platos_public(db: Session = Depends(get_db)):
    """Obtener lista de platos (público)"""
    platos = db.query(Plato).filter(Plato.activo == True).all()
    return platos


@router.get("/", response_model=List[MenuResponse])
def get_menus_public(db: Session = Depends(get_db)):
    """Obtener lista de menús (público)"""
    menus = db.query(Menu).filter(Menu.activo == True).order_by(Menu.fecha.desc()).all()
    return menus


@router.get("/hoy/")
def get_menu_hoy_public(db: Session = Depends(get_db)):
    """Obtener menú de hoy (público)"""
    from datetime import date
    today = date.today()
    
    menu = db.query(Menu).filter(
        Menu.fecha == today,
        Menu.activo == True
    ).first()
    
    if not menu:
        return {"message": "No hay menú para hoy"}
    
    return menu


@router.get("/stats/")
def get_menu_stats_public(db: Session = Depends(get_db)):
    """Obtener estadísticas del sistema (público)"""
    from datetime import date
    
    # Contar platos
    total_platos = db.query(Plato).count()
    platos_activos = db.query(Plato).filter(Plato.activo == True).count()
    platos_fijos = db.query(Plato).filter(Plato.tipo == 'Fijo', Plato.activo == True).count()
    platos_variables = db.query(Plato).filter(Plato.tipo == 'Variable', Plato.activo == True).count()
    
    # Contar menús
    total_menus = db.query(Menu).count()
    menus_activos = db.query(Menu).filter(Menu.activo == True).count()
    
    # Verificar si hay menú para hoy
    today = date.today()
    menu_hoy = db.query(Menu).filter(Menu.fecha == today, Menu.activo == True).first()
    tiene_menu_hoy = menu_hoy is not None
    
    return {
        "platos": {
            "total": total_platos,
            "activos": platos_activos,
            "fijos": platos_fijos,
            "variables": platos_variables
        },
        "menus": {
            "total": total_menus,
            "activos": menus_activos,
            "tiene_menu_hoy": tiene_menu_hoy
        },
        "sistema": {
            "estado": "funcionando",
            "version": "1.0.0"
        }
    }
