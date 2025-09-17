"""
Router para el sistema de menú del día
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.dependencies import get_current_user
from app.services.menu_service import MenuService
from app.schemas.menu import (
    MenuDayCreate, MenuDayResponse, MenuDayWithCategories,
    CategoriaMenuCreate, CategoriaMenuResponse,
    OpcionMenuCreate, OpcionMenuResponse,
    MenuItemCreate, MenuItemResponse, OrderWithMenuItems
)

router = APIRouter(prefix="/menu", tags=["menú"])


# ============================================================================
# ENDPOINTS PARA ADMIN/COCINA - GESTIÓN DE MENÚS
# ============================================================================

@router.post("/", response_model=MenuDayResponse)
def create_menu_day(
    menu_data: MenuDayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear un nuevo menú del día (ADMIN/COCINA)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.COCINA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y personal de cocina pueden crear menús"
        )
    
    try:
        menu = MenuService.create_menu_day(db, menu_data)
        return menu
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/today", response_model=MenuDayWithCategories)
def get_today_menu(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener el menú del día actual"""
    menu = MenuService.get_today_menu(db)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay menú disponible para hoy"
        )
    
    # Obtener menú con opciones agrupadas por categoría
    menu_with_categories = MenuService.get_menu_with_categories(db, menu.id)
    if not menu_with_categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error al obtener el menú"
        )
    
    return menu_with_categories


@router.get("/", response_model=List[MenuDayResponse])
def get_all_menus(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todos los menús (ADMIN/COCINA)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.COCINA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y personal de cocina pueden ver todos los menús"
        )
    
    menus = MenuService.get_all_menus(db, limit)
    return menus


@router.get("/{fecha}", response_model=MenuDayWithCategories)
def get_menu_by_date(
    fecha: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener menú por fecha específica"""
    menu = MenuService.get_menu_by_date(db, fecha)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay menú disponible para la fecha {fecha}"
        )
    
    menu_with_categories = MenuService.get_menu_with_categories(db, menu.id)
    if not menu_with_categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error al obtener el menú"
        )
    
    return menu_with_categories


# ============================================================================
# ENDPOINTS PARA GESTIÓN DE CATEGORÍAS
# ============================================================================

@router.post("/categorias", response_model=CategoriaMenuResponse)
def create_categoria(
    categoria_data: CategoriaMenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear una nueva categoría de menú (ADMIN/COCINA)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.COCINA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y personal de cocina pueden crear categorías"
        )
    
    try:
        categoria = MenuService.create_categoria(db, categoria_data)
        return categoria
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando categoría: {str(e)}"
        )


@router.get("/categorias", response_model=List[CategoriaMenuResponse])
def get_all_categorias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todas las categorías de menú"""
    categorias = MenuService.get_all_categorias(db)
    return categorias


@router.post("/{menu_id}/opciones", response_model=OpcionMenuResponse)
def add_opcion_to_menu(
    menu_id: int,
    opcion_data: OpcionMenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Agregar opción a un menú existente (ADMIN/COCINA)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.COCINA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y personal de cocina pueden agregar opciones"
        )
    
    try:
        opcion = MenuService.add_opcion_to_menu(db, menu_id, opcion_data)
        return opcion
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# ENDPOINTS PARA MESEROS - CREAR PEDIDOS CON MENÚ
# ============================================================================

@router.post("/pedidos", response_model=OrderWithMenuItems)
def create_order_with_menu(
    table_id: Optional[int],
    menu_items: List[MenuItemCreate],
    customer_name: Optional[str] = None,
    customer_phone: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear pedido con items de menú (MESERO)"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros pueden crear pedidos"
        )
    
    try:
        # Convertir MenuItemCreate a dict para el servicio
        menu_items_dict = []
        for item in menu_items:
            menu_items_dict.append({
                'menu_id': item.menu_id,
                'categoria_id': item.categoria_id,
                'opcion_id': item.opcion_id,
                'quantity': item.quantity,
                'observaciones': item.observaciones
            })
        
        order = MenuService.create_order_with_menu_items(
            db=db,
            waiter_id=current_user.id,
            table_id=table_id,
            menu_items=menu_items_dict,
            customer_name=customer_name,
            customer_phone=customer_phone,
            notes=notes
        )
        
        # Obtener el pedido completo con relaciones
        db.refresh(order)
        return order
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# ENDPOINTS PARA COCINA - GESTIÓN DE ESTADOS
# ============================================================================

@router.get("/pedidos/estado/{estado}", response_model=List[OrderWithMenuItems])
def get_orders_by_estado_cocina(
    estado: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener pedidos por estado de cocina (COCINA/ADMIN)"""
    if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo personal de cocina puede ver pedidos por estado"
        )
    
    # Validar estados permitidos
    estados_validos = ['Pendiente', 'En preparación', 'Listo para servir', 'Servido']
    if estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Estados permitidos: {', '.join(estados_validos)}"
        )
    
    orders = MenuService.get_orders_by_estado_cocina(db, estado)
    return orders


@router.patch("/pedidos/{order_id}/estado")
def update_order_estado_cocina(
    order_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar estado de cocina de un pedido (COCINA/ADMIN)"""
    if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo personal de cocina puede actualizar estados"
        )
    
    # Validar estados permitidos
    estados_validos = ['Pendiente', 'En preparación', 'Listo para servir', 'Servido']
    if nuevo_estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Estados permitidos: {', '.join(estados_validos)}"
        )
    
    order = MenuService.update_order_estado_cocina(db, order_id, nuevo_estado)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    return {
        "message": f"Estado del pedido {order.order_number} actualizado a {nuevo_estado}",
        "order_id": order.id,
        "order_number": order.order_number,
        "estado_cocina": order.estado_cocina
    }


# ============================================================================
# ENDPOINTS DE INFORMACIÓN GENERAL
# ============================================================================

@router.get("/info/estados")
def get_estados_cocina():
    """Obtener lista de estados de cocina disponibles"""
    return {
        "estados": [
            {"valor": "Pendiente", "descripcion": "Pedido recibido, esperando preparación"},
            {"valor": "En preparación", "descripcion": "Pedido en proceso de preparación"},
            {"valor": "Listo para servir", "descripcion": "Pedido terminado, listo para servir"},
            {"valor": "Servido", "descripcion": "Pedido ya servido al cliente"}
        ]
    }


