"""
Router para gestión de cocina - Vista unificada
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderItem
from app.models.location import Table, TableStatus
from app.models.product import Product
from app.schemas.order import KitchenOrderResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/kitchen", tags=["cocina"])


@router.get("/orders", response_model=List[KitchenOrderResponse])
def get_kitchen_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener órdenes para la cocina"""
    # Solo personal de cocina y admin pueden ver esto
    if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el personal de cocina puede acceder a esta vista"
        )
    
    # Obtener órdenes pendientes y en preparación con relaciones cargadas
    orders = db.query(Order).options(
        joinedload(Order.table),
        joinedload(Order.waiter),
        joinedload(Order.items).joinedload(OrderItem.product)
    ).filter(
        Order.status.in_(["pendiente", "en_preparacion", "listo"])
    ).order_by(Order.priority.desc(), Order.created_at.asc()).all()
    
    kitchen_orders = []
    for order in orders:
        # Construir items con información del producto
        order_items = []
        for item in order.items:
            item_data = {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal),
                "special_instructions": item.special_instructions,
                "status": item.status,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "kitchen_start_time": item.kitchen_start_time,
                "kitchen_end_time": item.kitchen_end_time,
                "product": {
                    "id": item.product.id,
                    "name": item.product.name,
                    "description": item.product.description,
                    "price": float(item.product.price) if item.product.price else 0.0
                } if item.product else None
            }
            order_items.append(item_data)
        
        # Convertir a diccionario para evitar problemas de validación
        kitchen_order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "table_number": str(order.table.table_number) if order.table else "N/A",
            "waiter_name": order.waiter.full_name if order.waiter else "N/A",
            "people_count": order.people_count,
            "status": order.status,
            "priority": order.priority,
            "notes": order.notes,
            "kitchen_notes": order.kitchen_notes,
            "created_at": order.created_at,
            "kitchen_start_time": order.kitchen_start_time,
            "kitchen_end_time": order.kitchen_end_time,
            "items": order_items
        }
        kitchen_orders.append(kitchen_order_dict)
    
    return kitchen_orders


@router.put("/orders/{order_id}/start")
def start_order_preparation(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Iniciar preparación de orden"""
    if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el personal de cocina puede iniciar preparación"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    if order.status != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden iniciar órdenes pendientes"
        )
    
    order.status = "en_preparacion"
    order.kitchen_start_time = datetime.now()
    
    # Marcar items como en preparación
    for item in order.items:
        item.status = "en_preparacion"
        item.kitchen_start_time = datetime.now()
    
    db.commit()
    db.refresh(order)
    
    return {"message": "Orden iniciada en preparación", "order_id": order.id}


@router.put("/orders/{order_id}/complete")
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Completar orden"""
    if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el personal de cocina puede completar órdenes"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    if order.status != "en_preparacion":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden completar órdenes en preparación"
        )
    
    order.status = "listo"
    order.kitchen_end_time = datetime.now()
    
    # Marcar items como listos
    for item in order.items:
        item.status = "listo"
        item.kitchen_end_time = datetime.now()
    
    db.commit()
    db.refresh(order)
    
    return {"message": "Orden completada", "order_id": order.id}


@router.put("/orders/{order_id}/notes")
def update_kitchen_notes(
    order_id: int,
    notes: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar notas de cocina"""
    if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el personal de cocina puede actualizar notas"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    kitchen_notes = notes.get('kitchen_notes', '')
    order.kitchen_notes = kitchen_notes
    
    db.commit()
    db.refresh(order)
    
    return {"message": "Notas actualizadas", "order_id": order.id}


@router.get("/stats")
def get_kitchen_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas de cocina"""
    if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el personal de cocina puede ver estadísticas"
        )
    
    # Contar órdenes por estado
    pending_orders = db.query(Order).filter(Order.status == "pendiente").count()
    preparing_orders = db.query(Order).filter(Order.status == "en_preparacion").count()
    ready_orders = db.query(Order).filter(Order.status == "listo").count()
    
    # Órdenes urgentes
    urgent_orders = db.query(Order).filter(
        and_(
            Order.status.in_(["pendiente", "en_preparacion"]),
            Order.priority.in_(["alta", "urgente"])
        )
    ).count()
    
    return {
        "pending_orders": pending_orders,
        "preparing_orders": preparing_orders,
        "ready_orders": ready_orders,
        "urgent_orders": urgent_orders,
        "total_active": pending_orders + preparing_orders + ready_orders
    }
