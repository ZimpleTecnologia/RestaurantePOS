"""
Router para el manejo de pedidos del restaurante
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.auth import get_current_active_user
from app.services.order_service import OrderService
from app.models.order import OrderStatus, OrderType

router = APIRouter(prefix="/orders", tags=["orders"])


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1
    unit_price: Optional[Decimal] = None
    notes: Optional[str] = None
    special_instructions: Optional[str] = None

class OrderCreate(BaseModel):
    table_id: Optional[int] = None
    customer_id: Optional[int] = None
    order_type: OrderType = OrderType.DINE_IN
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItemCreate]

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: OrderStatus
    order_type: OrderType
    total_amount: Decimal
    final_amount: Decimal
    created_at: str
    table_name: Optional[str] = None
    waiter_name: str
    items_count: int

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS DE PEDIDOS
# ============================================================================

@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear un nuevo pedido"""
    try:
        # Crear el pedido
        order = OrderService.create_order(
            db=db,
            waiter_id=current_user.id,
            table_id=order_data.table_id,
            customer_id=order_data.customer_id,
            order_type=order_data.order_type,
            customer_name=order_data.customer_name,
            customer_phone=order_data.customer_phone,
            notes=order_data.notes
        )
        
        # Agregar items al pedido
        for item_data in order_data.items:
            OrderService.add_item_to_order(
                db=db,
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                notes=item_data.notes,
                special_instructions=item_data.special_instructions
            )
        
        # Obtener el pedido actualizado
        order = OrderService.get_order_by_id(db, order.id)
        
        return {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "order_type": order.order_type,
            "total_amount": order.total_amount,
            "final_amount": order.final_amount,
            "created_at": order.created_at.isoformat(),
            "table_name": order.table.name if order.table else None,
            "waiter_name": order.waiter.full_name,
            "items_count": len(order.items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando pedido: {str(e)}"
        )

@router.get("/", response_model=List[OrderResponse])
def get_orders(
    status: Optional[OrderStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener pedidos"""
    if status:
        if status == OrderStatus.PENDING:
            orders = OrderService.get_pending_orders(db)
        elif status == OrderStatus.READY:
            orders = OrderService.get_ready_orders(db)
        elif status == OrderStatus.SERVED:
            orders = OrderService.get_pending_payment_orders(db)
        else:
            orders = OrderService.get_active_orders(db)
    else:
        orders = OrderService.get_active_orders(db)
    
    return [
        {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "order_type": order.order_type,
            "total_amount": order.total_amount,
            "final_amount": order.final_amount,
            "created_at": order.created_at.isoformat(),
            "table_name": order.table.name if order.table else None,
            "waiter_name": order.waiter.full_name,
            "items_count": len(order.items)
        }
        for order in orders
    ]

@router.get("/pending", response_model=List[OrderResponse])
def get_pending_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener pedidos pendientes (para cocina)"""
    orders = OrderService.get_pending_orders(db)
    return [
        {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "order_type": order.order_type,
            "total_amount": order.total_amount,
            "final_amount": order.final_amount,
            "created_at": order.created_at.isoformat(),
            "table_name": order.table.name if order.table else None,
            "waiter_name": order.waiter.full_name,
            "items_count": len(order.items)
        }
        for order in orders
    ]

@router.get("/ready", response_model=List[OrderResponse])
def get_ready_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener pedidos listos para servir"""
    orders = OrderService.get_ready_orders(db)
    return [
        {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "order_type": order.order_type,
            "total_amount": order.total_amount,
            "final_amount": order.final_amount,
            "created_at": order.created_at.isoformat(),
            "table_name": order.table.name if order.table else None,
            "waiter_name": order.waiter.full_name,
            "items_count": len(order.items)
        }
        for order in orders
    ]

@router.get("/pending-payment", response_model=List[OrderResponse])
def get_pending_payment_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener pedidos pendientes de pago"""
    orders = OrderService.get_pending_payment_orders(db)
    return [
        {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "order_type": order.order_type,
            "total_amount": order.total_amount,
            "final_amount": order.final_amount,
            "created_at": order.created_at.isoformat(),
            "table_name": order.table.name if order.table else None,
            "waiter_name": order.waiter.full_name,
            "items_count": len(order.items)
        }
        for order in orders
    ]

@router.get("/{order_id}")
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener detalles completos de un pedido"""
    order_details = OrderService.get_order_details(db, order_id)
    if not order_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    return order_details

@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar estado de un pedido"""
    order = OrderService.update_order_status(db, order_id, status_update.status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    return {
        "message": f"Pedido {order.order_number} actualizado a {status_update.status}",
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "table_name": order.table.name if order.table else None
        }
    }

@router.post("/{order_id}/mark-preparing")
def mark_order_as_preparing(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Marcar pedido como en preparación"""
    order = OrderService.mark_order_as_preparing(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    return {
        "message": f"Pedido {order.order_number} marcado como en preparación",
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status
        }
    }

@router.post("/{order_id}/mark-ready")
def mark_order_as_ready(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Marcar pedido como listo"""
    order = OrderService.mark_order_as_ready(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    return {
        "message": f"Pedido {order.order_number} marcado como listo",
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status
        }
    }

@router.post("/{order_id}/mark-served")
def mark_order_as_served(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Marcar pedido como servido"""
    order = OrderService.mark_order_as_served(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    return {
        "message": f"Pedido {order.order_number} marcado como servido",
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status
        }
    }

@router.post("/{order_id}/mark-paid")
def mark_order_as_paid(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Marcar pedido como pagado"""
    order = OrderService.mark_order_as_paid(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    return {
        "message": f"Pedido {order.order_number} marcado como pagado",
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status
        }
    }

@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancelar un pedido"""
    order = OrderService.cancel_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    return {
        "message": f"Pedido {order.order_number} cancelado exitosamente",
        "order": {
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status
        }
    }

@router.get("/summary/today")
def get_orders_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener resumen de pedidos del día"""
    summary = OrderService.get_orders_summary(db)
    return summary
