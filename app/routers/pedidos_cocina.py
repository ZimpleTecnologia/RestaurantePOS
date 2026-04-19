"""
Router para gestión de pedidos en cocina (KDS - Kitchen Display System)
Módulo de Pedidos a Cocina - Vista de Cocina
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderItem, OrderStatus, OrderItemOption
from app.schemas.order import (
    OrderResponse, KitchenOrderResponse
)
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/pedidos-cocina", tags=["Pedidos Cocina"])


def require_cocina_or_admin(current_user: User = Depends(get_current_active_user)):
    """Verificar que el usuario sea cocina o admin"""
    if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el personal de cocina y administradores pueden acceder a esta funcionalidad"
        )
    return current_user


@router.get("/pedidos", response_model=List[KitchenOrderResponse], summary="Listar pedidos para cocina")
def listar_pedidos_cocina(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cocina_or_admin)
):
    """
    Listar pedidos activos para cocina.
    Filtra por estados: CONFIRMED, PREPARING, READY.
    """
    estados_activos = [
        OrderStatus.CONFIRMED,
        OrderStatus.PREPARING,
        OrderStatus.READY
    ]
    
    pedidos = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.opciones)
    ).filter(
        Order.status.in_(estados_activos)
    ).order_by(
        Order.created_at.asc()
    ).all()
    
    resultado = []
    for pedido in pedidos:
        tab_name = pedido.table.name if pedido.table else "N/A"
        waiter_name = pedido.waiter.full_name if pedido.waiter else "N/A"
        
        resultado.append(KitchenOrderResponse(
            id=pedido.id,
            order_number=pedido.order_number,
            table_name=tab_name,
            waiter_name=waiter_name,
            status=pedido.status,
            created_at=pedido.created_at,
            hora_envio=pedido.hora_envio,
            notes=pedido.notes,
            items=[
                {
                    "item_type": item.item_type,
                    "quantity": item.quantity,
                    "snapshot_name": item.snapshot_name or "Producto",
                    "special_instructions": item.special_instructions,
                    "opciones": [
                        {
                            "categoria": opt.categoria,
                            "opcion_elegida": opt.opcion_elegida
                        } for opt in item.opciones
                    ]
                } for item in pedido.items
            ]
        ))
    
    return resultado


@router.put("/pedidos/{pedido_id}/estado", response_model=KitchenOrderResponse)
def cambiar_estado_pedido(
    pedido_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cocina_or_admin)
):
    """Cambiar el estado de un pedido desde cocina"""
    pedido = db.query(Order).filter(Order.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        estado_enum = OrderStatus(nuevo_estado.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Estado inválido: {nuevo_estado}")
    
    if estado_enum == OrderStatus.PREPARING:
        if pedido.status != OrderStatus.CONFIRMED:
             raise HTTPException(status_code=400, detail="Solo se puede pasar a PREPARANDO desde CONFIRMADO")
        pedido.status = OrderStatus.PREPARING
        pedido.kitchen_start_time = datetime.now()
    
    elif estado_enum == OrderStatus.READY:
        if pedido.status not in [OrderStatus.CONFIRMED, OrderStatus.PREPARING]:
             raise HTTPException(status_code=400, detail="Solo se puede pasar a LISTO desde CONFIRMADO o PREPARANDO")
        pedido.status = OrderStatus.READY
        pedido.kitchen_end_time = datetime.now()
    
    else:
        raise HTTPException(status_code=400, detail="Estado no permitido para cocina")
        
    db.commit()
    db.refresh(pedido)
    
    return KitchenOrderResponse(
        id=pedido.id,
        order_number=pedido.order_number,
        table_name=pedido.table.name if pedido.table else "N/A",
        waiter_name=pedido.waiter.full_name if pedido.waiter else "N/A",
        status=pedido.status,
        created_at=pedido.created_at,
        hora_envio=pedido.hora_envio,
        items=[]
    )


@router.get("/estadisticas", summary="Obtener estadísticas de cocina")
def obtener_estadisticas_cocina(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_cocina_or_admin)
):
    """
    Obtener estadísticas de pedidos en cocina basándose en el modelo Order.
    """
    pedidos_confirmados = db.query(Order).filter(
        Order.status == OrderStatus.CONFIRMED
    ).count()
    
    pedidos_en_preparacion = db.query(Order).filter(
        Order.status == OrderStatus.PREPARING
    ).count()

    pedidos_listos = db.query(Order).filter(
        Order.status == OrderStatus.READY
    ).count()
    
    return {
        "confirmados": pedidos_confirmados,
        "en_preparacion": pedidos_en_preparacion,
        "listos": pedidos_listos,
        "total_activos": pedidos_confirmados + pedidos_en_preparacion + pedidos_listos
    }
