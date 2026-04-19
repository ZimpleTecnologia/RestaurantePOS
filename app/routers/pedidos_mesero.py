"""
Router para gestión de pedidos por meseros
Módulo de Pedidos a Cocina - Vista de Meseros
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, date
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.location import Table, TableStatus
from app.models.order import Order, OrderItem, OrderStatus, OrderType, ItemType, OrderItemOption
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderStatsResponse
)
from app.services.order_service import OrderService
from app.services.table_service import TableService
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/pedidos-mesero", tags=["Pedidos Mesero"])


def require_mesero_or_admin(current_user: User = Depends(get_current_active_user)):
    """Verificar que el usuario sea mesero o admin"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros y administradores pueden acceder a esta funcionalidad"
        )
    return current_user


@router.get("/mesas", summary="Listar mesas disponibles")
def listar_mesas(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mesero_or_admin)
):
    """
    Lista todas las mesas con su estado actual.
    Indica si tienen pedidos activos.
    """
    mesas = db.query(Table).filter(Table.is_active == True).all()
    
    resultado = []
    for mesa in mesas:
        # Buscar pedido activo (BORRADOR o PENDIENTE/CONFIRMADO) para esta mesa
        pedido_activo = db.query(Order).filter(
            and_(
                Order.table_id == mesa.id,
                Order.status.in_([OrderStatus.DRAFT, OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING])
            )
        ).first()
        
        estado_mesa = "libre"
        if pedido_activo:
            if pedido_activo.status == OrderStatus.DRAFT:
                estado_mesa = "con_pedido_en_curso"
            else:
                estado_mesa = "con_pedido_en_cocina"
        elif mesa.status == TableStatus.OCCUPIED:
            estado_mesa = "ocupada"
        
        resultado.append({
            "id": mesa.id,
            "nombre": mesa.name,
            "numero": mesa.table_number,
            "capacidad": mesa.capacity,
            "estado_mesa": estado_mesa,
            "tiene_pedido_activo": pedido_activo is not None,
            "pedido_id": pedido_activo.id if pedido_activo else None
        })
    
    return {"mesas": resultado}


@router.post("/pedidos", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mesero_or_admin)
):
    """
    Crear un nuevo pedido en estado BORRADOR.
    """
    # Verificar que la mesa existe y está activa
    mesa = db.query(Table).filter(Table.id == pedido_data.table_id, Table.is_active == True).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa no encontrada o inactiva")
    
    # Crear pedido usando el servicio unificado
    order = OrderService.create_order(
        db=db,
        waiter_id=current_user.id,
        table_id=pedido_data.table_id,
        order_type=OrderType.DINE_IN,
        status=OrderStatus.DRAFT,
        notes=pedido_data.notes
    )
    
    # Agregar items
    for item_data in pedido_data.items:
        opciones_mapped = [opt.dict() for opt in item_data.opciones] if item_data.opciones else []
        OrderService.add_item_to_order(
            db=db,
            order_id=order.id,
            item_type=item_data.item_type,
            product_id=item_data.product_id,
            menu_id=item_data.menu_id,
            plato_id=item_data.plato_id,
            quantity=item_data.quantity,
            notes=item_data.notes,
            special_instructions=item_data.special_instructions,
            opciones=opciones_mapped
        )
    
    return order


@router.get("/pedidos/{pedido_id}", response_model=OrderResponse)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mesero_or_admin)
):
    """Obtener un pedido específico"""
    pedido = OrderService.get_order_by_id(db, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    return pedido


@router.get("/pedidos/mesa/{mesa_id}", response_model=Optional[OrderResponse])
def obtener_pedido_activo_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mesero_or_admin)
):
    """Obtener el pedido activo (BORRADOR) de una mesa"""
    pedido = db.query(Order).filter(
        and_(
            Order.table_id == mesa_id,
            Order.status == OrderStatus.DRAFT
        )
    ).first()
    return pedido


@router.post("/pedidos/{pedido_id}/enviar-cocina", response_model=OrderResponse)
def enviar_pedido_cocina(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mesero_or_admin)
):
    """Confirmar y enviar pedido a cocina"""
    pedido = db.query(Order).filter(Order.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if pedido.status != OrderStatus.DRAFT:
        raise HTTPException(status_code=400, detail="El pedido ya no está en borrador")
    
    # Cambiar estado a CONFIRMADO (para que cocina lo gestione)
    pedido.status = OrderStatus.CONFIRMED
    pedido.hora_envio = datetime.now()
    
    # Ocupar mesa formalmente
    if pedido.table_id:
        TableService.occupy_table(db, pedido.table_id)
        
    db.commit()
    db.refresh(pedido)
    return pedido


@router.get("/pedidos", response_model=List[OrderResponse])
def listar_pedidos_mesero(
    estado: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mesero_or_admin)
):
    """Listar pedidos filtrados por estado"""
    query = db.query(Order).order_by(Order.created_at.desc())
    if estado:
        query = query.filter(Order.status == estado.lower())
    return query.all()


@router.get("/estadisticas", response_model=OrderStatsResponse)
def obtener_estadisticas_mesero(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mesero_or_admin)
):
    """Estadísticas de órdenes para el dashboard del mesero"""
    hoy = datetime.now().date()
    query_hoy = db.query(Order).filter(func.date(Order.created_at) == hoy)
    
    return OrderStatsResponse(
        total=query_hoy.count(),
        pendientes=query_hoy.filter(Order.status == OrderStatus.PENDING).count(),
        en_preparacion=query_hoy.filter(Order.status == OrderStatus.PREPARING).count(),
        listos=query_hoy.filter(Order.status == OrderStatus.READY).count(),
        confirmados=query_hoy.filter(Order.status == OrderStatus.CONFIRMED).count(),
        pedidos_hoy=query_hoy.count()
    )


from app.models.restaurant_menu import MenuDia, PlatoRestaurante, MenuCategoriaPlato, CategoriaMenuRestaurante

@router.get("/menus-dia-activo", summary="Obtener menú del día activo")
def obtener_menu_dia_activo(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mesero_or_admin)
):
    """
    Obtener el menú del día activo con sus categorías y opciones.
    """
    hoy = datetime.now().date()
    
    menu = db.query(MenuDia).filter(
        and_(
            MenuDia.fecha == hoy,
            MenuDia.estado == 'ACTIVE'
        )
    ).first()
    
    if not menu:
        return {"menu": None, "message": "No hay menú del día activo para hoy"}
    
    # Obtener categorías y platos vinculados a través de MenuCategoriaPlato
    menu_categorias = db.query(MenuCategoriaPlato).filter(
        and_(
            MenuCategoriaPlato.menu_dia_id == menu.id,
            MenuCategoriaPlato.activo == True
        )
    ).all()
    
    # Agrupar por categoría
    categorias_dict = {}
    for mcp in menu_categorias:
        categoria = db.query(CategoriaMenuRestaurante).filter(
            CategoriaMenuRestaurante.id == mcp.categoria_id
        ).first()
        
        plato = db.query(PlatoRestaurante).filter(
            PlatoRestaurante.id == mcp.plato_id
        ).first()
        
        if categoria:
            categoria_nombre = categoria.nombre
            if categoria_nombre not in categorias_dict:
                categorias_dict[categoria_nombre] = {
                    "id": categoria.id,
                    "nombre": categoria.nombre,
                    "descripcion": categoria.descripcion,
                    "platos": []
                }
            
            if plato and plato.activo:
                categorias_dict[categoria_nombre]["platos"].append({
                    "id": plato.id,
                    "nombre": plato.nombre,
                    "descripcion": plato.descripcion
                })
    
    return {
        "menu": {
            "id": menu.id,
            "nombre": menu.nombre,
            "fecha": menu.fecha.isoformat(),
            "precio": float(menu.precio),
            "descripcion": menu.descripcion,
            "categorias": list(categorias_dict.values())
        }
    }


@router.get("/platos-especiales", summary="Listar platos especiales activos")
def listar_platos_especiales(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mesero_or_admin)
):
    """
    Listar todos los platos especiales activos.
    """
    platos = db.query(PlatoRestaurante).filter(
        and_(
            PlatoRestaurante.tipo == 'Plato_Fijo',
            PlatoRestaurante.activo == True
        )
    ).all()
    
    return {
        "platos": [
            {
                "id": plato.id,
                "nombre": plato.nombre,
                "descripcion": plato.descripcion,
                "precio": float(plato.precio)
            }
            for plato in platos
        ]
    }

