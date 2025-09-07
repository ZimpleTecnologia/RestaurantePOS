"""
Router específico para meseros - Optimizado para toma de pedidos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderItem, OrderStatus, OrderType
from app.models.location import Table, TableStatus
from app.models.product import Product
from app.auth.dependencies import get_current_active_user
from app.services.order_service import OrderService

router = APIRouter(prefix="/waiters", tags=["meseros"])


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class QuickOrderItem(BaseModel):
    product_id: int
    quantity: int = 1
    notes: Optional[str] = None

class QuickOrderCreate(BaseModel):
    table_id: int
    items: List[QuickOrderItem]
    notes: Optional[str] = None

class TableStatusResponse(BaseModel):
    id: int
    table_number: int
    status: str
    current_order: Optional[str] = None
    waiter_name: Optional[str] = None
    created_at: Optional[str] = None

class ProductQuickResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: bool = True

class ActiveOrderResponse(BaseModel):
    id: int
    order_number: str
    table_name: str
    waiter_name: str
    status: str
    total_amount: Decimal
    items_count: int
    created_at: str


# ============================================================================
# ENDPOINTS PARA MESEROS
# ============================================================================

@router.get("/tables/", response_model=List[TableStatusResponse])
def get_tables_for_waiters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estado de todas las mesas para meseros"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros pueden acceder a esta información"
        )
    
    # Obtener todas las mesas con información de pedidos activos
    tables = db.query(Table).all()
    
    table_statuses = []
    for table in tables:
        # Buscar pedido activo en esta mesa
        active_order = db.query(Order).filter(
            and_(
                Order.table_id == table.id,
                Order.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.SERVED])
            )
        ).first()
        
        table_status = {
            "id": table.id,
            "table_number": table.table_number,
            "status": table.status,
            "current_order": active_order.order_number if active_order else None,
            "waiter_name": active_order.waiter.full_name if active_order and active_order.waiter else None,
            "created_at": active_order.created_at.isoformat() if active_order else None
        }
        table_statuses.append(table_status)
    
    return table_statuses


@router.get("/products/", response_model=List[ProductQuickResponse])
def get_products_for_waiters(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener productos disponibles para meseros con filtros"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros pueden acceder a esta información"
        )
    
    query = db.query(Product).filter(Product.is_active == True)
    
    # Filtrar por categoría
    if category:
        query = query.filter(Product.category == category)
    
    # Filtrar por búsqueda
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    
    products = query.order_by(Product.name).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "category": p.category,
            "image_url": p.image_url,
            "is_available": p.stock_quantity > 0 if p.track_stock else True
        }
        for p in products
    ]


@router.get("/products/categories")
def get_product_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener categorías de productos disponibles"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros pueden acceder a esta información"
        )
    
    categories = db.query(Product.category).filter(
        and_(
            Product.category.isnot(None),
            Product.category != "",
            Product.is_active == True
        )
    ).distinct().all()
    
    return [cat[0] for cat in categories if cat[0]]


@router.post("/orders/quick", response_model=dict)
def create_quick_order(
    order_data: QuickOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear pedido rápido para meseros"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros pueden crear pedidos"
        )
    
    # Verificar que la mesa existe y está disponible
    table = db.query(Table).filter(Table.id == order_data.table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    # Verificar que no hay pedido activo en la mesa
    active_order = db.query(Order).filter(
        and_(
            Order.table_id == order_data.table_id,
            Order.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.SERVED])
        )
    ).first()
    
    if active_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un pedido activo en esta mesa: #{active_order.order_number}"
        )
    
    try:
        # Crear el pedido
        order = OrderService.create_order(
            db=db,
            waiter_id=current_user.id,
            table_id=order_data.table_id,
            order_type=OrderType.DINE_IN,
            notes=order_data.notes
        )
        
        # Agregar items al pedido
        for item_data in order_data.items:
            # Verificar que el producto existe y está disponible
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con ID {item_data.product_id} no encontrado"
                )
            
            if not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Producto '{product.name}' no está disponible"
                )
            
            OrderService.add_item_to_order(
                db=db,
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=product.price,
                notes=item_data.notes
            )
        
        # Actualizar estado de la mesa
        table.status = TableStatus.OCCUPIED
        db.commit()
        
        # Obtener el pedido actualizado
        order = OrderService.get_order_by_id(db, order.id)
        
        return {
            "success": True,
            "message": f"Pedido #{order.order_number} creado exitosamente",
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "table_number": table.table_number,
                "total_amount": float(order.total_amount),
                "items_count": len(order.items)
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando pedido: {str(e)}"
        )


@router.get("/orders/active", response_model=List[ActiveOrderResponse])
def get_active_orders_for_waiters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener pedidos activos para el mesero actual"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros pueden acceder a esta información"
        )
    
    # Si es mesero, solo ver sus pedidos. Si es admin/supervisor, ver todos
    if current_user.role == UserRole.MESERO:
        orders = db.query(Order).filter(
            and_(
                Order.waiter_id == current_user.id,
                Order.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.SERVED])
            )
        ).all()
    else:
        orders = db.query(Order).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.SERVED])
        ).all()
    
    active_orders = []
    for order in orders:
        active_order = {
            "id": order.id,
            "order_number": order.order_number,
            "table_name": f"Mesa {order.table.table_number}" if order.table else "N/A",
            "waiter_name": order.waiter.full_name,
            "status": order.status,
            "total_amount": order.total_amount,
            "items_count": len(order.items),
            "created_at": order.created_at.isoformat()
        }
        active_orders.append(active_order)
    
    return active_orders


@router.put("/orders/{order_id}/serve")
def mark_order_as_served(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Marcar pedido como servido"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros pueden marcar pedidos como servidos"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    # Verificar que el mesero es el dueño del pedido o es admin
    if current_user.role == UserRole.MESERO and order.waiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes marcar como servidos tus propios pedidos"
        )
    
    if order.status != OrderStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden marcar como servidos pedidos que estén listos"
        )
    
    order.status = OrderStatus.SERVED
    order.served_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": f"Pedido #{order.order_number} marcado como servido"
    }


@router.put("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancelar pedido"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros pueden cancelar pedidos"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    # Verificar que el mesero es el dueño del pedido o es admin
    if current_user.role == UserRole.MESERO and order.waiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes cancelar tus propios pedidos"
        )
    
    if order.status in [OrderStatus.PAID, OrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar un pedido ya pagado o cancelado"
        )
    
    order.status = OrderStatus.CANCELLED
    order.notes = f"Cancelado por {current_user.full_name}. Razón: {reason}" if reason else f"Cancelado por {current_user.full_name}"
    db.commit()
    
    # Liberar mesa si es pedido en mesa
    if order.table_id:
        table = db.query(Table).filter(Table.id == order.table_id).first()
        if table:
            table.status = TableStatus.AVAILABLE
            db.commit()
    
    return {
        "success": True,
        "message": f"Pedido #{order.order_number} cancelado exitosamente"
    }


@router.get("/orders/{order_id}/details")
def get_order_details_for_waiters(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener detalles completos de un pedido"""
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo meseros pueden ver detalles de pedidos"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    # Verificar que el mesero es el dueño del pedido o es admin
    if current_user.role == UserRole.MESERO and order.waiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes ver detalles de tus propios pedidos"
        )
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "table_name": f"Mesa {order.table.table_number}" if order.table else "N/A",
        "waiter_name": order.waiter.full_name,
        "status": order.status,
        "total_amount": float(order.total_amount),
        "tax_amount": float(order.tax_amount),
        "discount_amount": float(order.discount_amount),
        "final_amount": float(order.final_amount),
        "notes": order.notes,
        "created_at": order.created_at.isoformat(),
        "served_at": order.served_at.isoformat() if order.served_at else None,
        "items": [
            {
                "id": item.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total_price": float(item.total_price),
                "notes": item.notes,
                "is_ready": item.is_ready,
                "is_served": item.is_served
            }
            for item in order.items
        ]
    }
