"""
Router para gestión de órdenes de restaurante
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderItem, OrderStatus, OrderPriority
from app.models.location import Table, TableStatus
from app.models.product import Product
from app.models.sale import Sale, SaleStatus
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, 
    KitchenOrderResponse, OrderItemUpdate
)
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["órdenes"])


def generate_order_number(db: Session) -> str:
    """Generar número de orden único"""
    from datetime import datetime
    import random
    
    today = datetime.now().strftime("%Y%m%d")
    last_order = db.query(Order).filter(
        Order.order_number.like(f"ORD-{today}-%")
    ).order_by(Order.id.desc()).first()
    
    if last_order:
        last_num = int(last_order.order_number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"ORD-{today}-{new_num:04d}"


@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva orden (solo meseros)"""
    # Verificar que el usuario sea mesero
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los meseros pueden crear órdenes"
        )
    
    # Verificar que la mesa existe y está disponible
    table = db.query(Table).filter(Table.id == order_data.table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    # Verificar que la mesa no tenga órdenes activas
    active_order = db.query(Order).filter(
        and_(
            Order.table_id == order_data.table_id,
            Order.status.in_([OrderStatus.pendiente, OrderStatus.en_preparacion, OrderStatus.listo])
        )
    ).first()
    
    if active_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La mesa ya tiene una orden activa"
        )
    
    # Crear la orden
    order_number = generate_order_number(db)
    db_order = Order(
        order_number=order_number,
        table_id=order_data.table_id,
        waiter_id=current_user.id,
        people_count=order_data.people_count,
        priority=order_data.priority,
        notes=order_data.notes
    )
    
    db.add(db_order)
    db.flush()  # Para obtener el ID de la orden
    
    # Agregar items
    total_amount = 0
    for item_data in order_data.items:
        # Verificar que el producto existe
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto {item_data.product_id} no encontrado"
            )
        
        subtotal = item_data.quantity * item_data.unit_price
        
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            subtotal=subtotal,
            special_instructions=item_data.special_instructions
        )
        
        db.add(order_item)
        total_amount += subtotal
    
    # Crear venta pendiente de pago
    from app.routers.sales import generate_sale_number
    sale_number = generate_sale_number(db)
    
    db_sale = Sale(
        sale_number=sale_number,
        user_id=current_user.id,
        table_id=order_data.table_id,
        total=total_amount,
        subtotal=total_amount,
        status=SaleStatus.PENDIENTE,
        notes=f"Orden automática: {order_number}"
    )
    
    db.add(db_sale)
    db.flush()
    
    # Vincular orden con venta
    db_order.sale_id = db_sale.id
    
    # Actualizar estado de la mesa
    table.status = TableStatus.OCUPADA
    
    db.commit()
    db.refresh(db_order)
    
    return db_order


@router.get("/", response_model=List[OrderResponse])
def get_orders(
    status: Optional[OrderStatus] = None,
    table_id: Optional[int] = None,
    waiter_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener órdenes con filtros"""
    query = db.query(Order)
    
    # Filtros
    if status:
        query = query.filter(Order.status == status)
    
    if table_id:
        query = query.filter(Order.table_id == table_id)
    
    if waiter_id:
        query = query.filter(Order.waiter_id == waiter_id)
    
    # Si es mesero, solo ver sus propias órdenes
    if current_user.role == UserRole.MESERO:
        query = query.filter(Order.waiter_id == current_user.id)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/kitchen", response_model=List[KitchenOrderResponse])
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
        Order.status.in_([OrderStatus.pendiente, OrderStatus.en_preparacion, OrderStatus.listo])
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
        
        kitchen_order = KitchenOrderResponse(
            id=order.id,
            order_number=order.order_number,
            table_number=str(order.table.table_number) if order.table else "N/A",
            waiter_name=order.waiter.full_name if order.waiter else "N/A",
            people_count=order.people_count,
            status=order.status,
            priority=order.priority,
            notes=order.notes,
            kitchen_notes=order.kitchen_notes,
            created_at=order.created_at,
            kitchen_start_time=order.kitchen_start_time,
            kitchen_end_time=order.kitchen_end_time,
            items=order_items
        )
        kitchen_orders.append(kitchen_order)
    
    return kitchen_orders


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar estado de orden"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    new_status = status_update.get('new_status')
    kitchen_notes = status_update.get('kitchen_notes')
    
    # Verificar permisos según el estado
    if new_status == OrderStatus.en_preparacion:
        if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el personal de cocina puede marcar como en preparación"
            )
        order.kitchen_start_time = datetime.now()
    
    elif new_status == OrderStatus.listo:
        if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el personal de cocina puede marcar como listo"
            )
        order.kitchen_end_time = datetime.now()
    
    elif new_status == OrderStatus.servido:
        if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los meseros pueden marcar como servido"
            )
        order.served_time = datetime.now()
        # Liberar la mesa
        order.table.status = TableStatus.LIBRE
    
    # Actualizar orden
    if new_status:
        order.status = new_status
    if kitchen_notes:
        order.kitchen_notes = kitchen_notes
    
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener orden específica"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    # Si es mesero, solo puede ver sus propias órdenes
    if current_user.role == UserRole.MESERO and order.waiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta orden"
        )
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar orden"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.MESERO and order.waiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar esta orden"
        )
    
    # No se puede modificar orden ya servida
    if order.status == OrderStatus.servido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una orden ya servida"
        )
    
    # Actualizar campos
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return order
