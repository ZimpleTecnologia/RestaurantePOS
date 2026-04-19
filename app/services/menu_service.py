"""
Servicio para el sistema de menú del día

DEPRECATED: Este servicio está deprecado. Usar las funciones del router restaurant_menu directamente.
"""
import warnings
warnings.warn(
    "El servicio 'app.services.menu_service' está deprecado. Use las funciones del router 'restaurant_menu' en su lugar.",
    DeprecationWarning,
    stacklevel=2
)

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal

from app.models.restaurant_menu import MenuDia, CategoriaMenuRestaurante


class MenuService:
    """Servicio para gestionar el sistema de menú del día - DEPRECATED"""
    
    @staticmethod
    def get_menu_by_date(db: Session, fecha: date) -> Optional[MenuDia]:
        """Obtener menú del día por fecha - DEPRECATED"""
        warnings.warn(
            "MenuService.get_menu_by_date está deprecado. Use el endpoint /restaurant-menu/menus/hoy del router.",
            DeprecationWarning,
            stacklevel=2
        )
        return db.query(MenuDia).filter(MenuDia.fecha == fecha).first()
    
    @staticmethod
    def get_active_menus(db: Session) -> List[MenuDia]:
        """Obtener menús activos - DEPRECATED"""
        warnings.warn(
            "MenuService.get_active_menus está deprecado.",
            DeprecationWarning,
            stacklevel=2
        )
        return db.query(MenuDia).filter(MenuDia.estado == "ACTIVE").all()
    
    @staticmethod
    def get_categorias(db: Session) -> List[CategoriaMenuRestaurante]:
        """Obtener todas las categorías - DEPRECATED"""
        warnings.warn(
            "MenuService.get_categorias está deprecado. Use el endpoint /restaurant-menu/categorias/ del router.",
            DeprecationWarning,
            stacklevel=2
        )
        return db.query(CategoriaMenuRestaurante).filter(CategoriaMenuRestaurante.is_active == True).all()
    
    @staticmethod
    def get_menu_today(db: Session) -> Optional[MenuDia]:
        """Obtener menú del día de hoy - DEPRECATED"""
        return MenuService.get_menu_by_date(db, date.today())
