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
from app.models.order import Order, OrderItem
from app.models.location import Table, TableStatus
from app.models.product import Product
from app.models.sale import Sale, SaleItem, SaleStatus
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, 
    KitchenOrderResponse, OrderItemUpdate, OrderItemCreate
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


def generate_sale_number(db: Session) -> str:
    """Generar número de venta único"""
    from datetime import datetime
    
    today = datetime.now().strftime("%Y%m%d")
    last_sale = db.query(Sale).filter(
        Sale.sale_number.like(f"VTA-{today}-%")
    ).order_by(Sale.id.desc()).first()
    
    if last_sale:
        last_num = int(last_sale.sale_number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"VTA-{today}-{new_num:04d}"


@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva orden (solo meseros)"""
    try:
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
                Order.status.in_(["pendiente", "en_preparacion", "listo"])
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
            
            # Usar el precio del producto si no se proporciona unit_price
            unit_price = item_data.unit_price if item_data.unit_price else (product.price or 0.0)
            subtotal = item_data.quantity * unit_price
            
            order_item = OrderItem(
                order_id=db_order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=unit_price,
                subtotal=subtotal,
                total=subtotal,  # Usar subtotal como total también
                special_instructions=item_data.special_instructions
            )
            
            db.add(order_item)
            total_amount += subtotal
    
        # La venta se creará cuando la orden se marque como servida
        # Por ahora solo creamos la orden sin venta
        
        # Actualizar estado de la mesa
        table.status = TableStatus.OCUPADA
        
        db.commit()
        db.refresh(db_order)
        
        # Cargar relaciones para la respuesta
        db_order = db.query(Order).options(
            joinedload(Order.items),
            joinedload(Order.waiter),
            joinedload(Order.table)
        ).filter(Order.id == db_order.id).first()
        
        # Convertir objetos SQLAlchemy a diccionarios para evitar problemas de validación
        order_dict = {
            "id": db_order.id,
            "order_number": db_order.order_number,
            "table_id": db_order.table_id,
            "waiter_id": db_order.waiter_id,
            "sale_id": db_order.sale_id,
            "people_count": db_order.people_count,
            "status": db_order.status,
            "priority": db_order.priority,
            "notes": db_order.notes,
            "kitchen_notes": db_order.kitchen_notes,
            "created_at": db_order.created_at,
            "updated_at": db_order.updated_at,
            "kitchen_start_time": db_order.kitchen_start_time,
            "kitchen_end_time": db_order.kitchen_end_time,
            "served_time": db_order.served_time,
            "items": [
                {
                    "id": item.id,
                    "order_id": item.order_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price) if item.unit_price else None,
                    "subtotal": float(item.subtotal) if item.subtotal else None,
                    "total": float(item.total) if item.total else None,
                    "status": item.status,
                    "special_instructions": item.special_instructions,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "kitchen_start_time": item.kitchen_start_time,
                    "kitchen_end_time": item.kitchen_end_time,
                    "product": {
                        "id": item.product.id,
                        "code": item.product.code,
                        "name": item.product.name,
                        "description": item.product.description,
                        "price": float(item.product.price) if item.product.price else None
                    } if item.product else None
                }
                for item in db_order.items
            ],
            "waiter": {
                "id": db_order.waiter.id,
                "username": db_order.waiter.username,
                "full_name": db_order.waiter.full_name,
                "role": db_order.waiter.role
            } if db_order.waiter else None,
            "table": {
                "id": db_order.table.id,
                "table_number": db_order.table.table_number,
                "status": db_order.table.status
            } if db_order.table else None
        }
        
        return order_dict
        
    except Exception as e:
        db.rollback()
        import traceback
        print(f"Error al crear orden: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Args del error: {e.args}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la orden: {str(e)}"
        )


@router.get("/")
def get_orders(
    status: Optional[str] = None,
    table_id: Optional[int] = None,
    waiter_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener órdenes con filtros"""
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.waiter),
        joinedload(Order.table)
    )
    
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
    
    # Convertir a diccionarios para evitar problemas de validación
    orders_list = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "order_number": order.order_number,
            "table_id": order.table_id,
            "waiter_id": order.waiter_id,
            "sale_id": order.sale_id,
            "people_count": order.people_count,
            "status": order.status,
            "priority": order.priority,
            "notes": order.notes,
            "kitchen_notes": order.kitchen_notes,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "kitchen_start_time": order.kitchen_start_time,
            "kitchen_end_time": order.kitchen_end_time,
            "served_time": order.served_time,
            "items": [
                {
                    "id": item.id,
                    "order_id": item.order_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price) if item.unit_price else None,
                    "subtotal": float(item.subtotal) if item.subtotal else None,
                    "total": float(item.total) if item.total else None,
                    "status": item.status,
                    "special_instructions": item.special_instructions,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "kitchen_start_time": item.kitchen_start_time,
                    "kitchen_end_time": item.kitchen_end_time,
                    "product": {
                        "id": item.product.id,
                        "code": item.product.code,
                        "name": item.product.name,
                        "description": item.product.description,
                        "price": float(item.product.price) if item.product.price else None
                    } if item.product else None
                }
                for item in order.items
            ],
            "waiter": {
                "id": order.waiter.id,
                "username": order.waiter.username,
                "email": order.waiter.email,
                "full_name": order.waiter.full_name,
                "role": order.waiter.role
            } if order.waiter else None,
            "table": {
                "id": order.table.id,
                "table_number": order.table.table_number,
                "capacity": order.table.capacity,
                "status": order.table.status,
                "name": order.table.name,
                "notes": order.table.notes
            } if order.table else None
        }
        orders_list.append(order_dict)
    
    return orders_list


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
    if new_status == "en_preparacion":
        if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el personal de cocina puede marcar como en preparación"
            )
        order.kitchen_start_time = datetime.now()
    
    elif new_status == "listo":
        if current_user.role not in [UserRole.COCINA, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el personal de cocina puede marcar como listo"
            )
        order.kitchen_end_time = datetime.now()
    
    elif new_status == "servido":
        if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los meseros pueden marcar como servido"
            )
        order.served_time = datetime.now()
        
        # Crear venta automáticamente cuando se marca como servida
        if not order.sale_id:
            # Calcular total de la orden
            total_amount = sum(item.subtotal for item in order.items)
            
            # Generar número de venta
            sale_number = generate_sale_number(db)
            
            # Crear la venta
            db_sale = Sale(
                sale_number=sale_number,
                user_id=order.waiter_id,
                table_id=order.table_id,
                total=total_amount,
                subtotal=total_amount,
                status="pendiente",
                notes=f"Venta automática de orden: {order.order_number}"
            )
            
            db.add(db_sale)
            db.flush()
            
            # Vincular orden con venta
            order.sale_id = db_sale.id
            
            # Crear items de venta basados en los items de la orden
            for order_item in order.items:
                sale_item = SaleItem(
                    sale_id=db_sale.id,
                    product_id=order_item.product_id,
                    quantity=order_item.quantity,
                    unit_price=order_item.unit_price,
                    total=order_item.subtotal
                )
                db.add(sale_item)
        
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


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener orden específica"""
    order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.waiter),
        joinedload(Order.table)
    ).filter(Order.id == order_id).first()
    
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
    
    # Convertir a diccionario para evitar problemas de validación
    order_dict = {
        "id": order.id,
        "order_number": order.order_number,
        "table_id": order.table_id,
        "waiter_id": order.waiter_id,
        "sale_id": order.sale_id,
        "people_count": order.people_count,
        "status": order.status,
        "priority": order.priority,
        "notes": order.notes,
        "kitchen_notes": order.kitchen_notes,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "kitchen_start_time": order.kitchen_start_time,
        "kitchen_end_time": order.kitchen_end_time,
        "served_time": order.served_time,
        "items": [
            {
                "id": item.id,
                "order_id": item.order_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price) if item.unit_price else None,
                "subtotal": float(item.subtotal) if item.subtotal else None,
                "total": float(item.total) if item.total else None,
                "status": item.status,
                "special_instructions": item.special_instructions,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "kitchen_start_time": item.kitchen_start_time,
                "kitchen_end_time": item.kitchen_end_time,
                "product": {
                    "id": item.product.id,
                    "code": item.product.code,
                    "name": item.product.name,
                    "description": item.product.description,
                    "price": float(item.product.price) if item.product.price else None
                } if item.product else None
            }
            for item in order.items
        ],
        "waiter": {
            "id": order.waiter.id,
            "username": order.waiter.username,
            "email": order.waiter.email,
            "full_name": order.waiter.full_name,
            "role": order.waiter.role
        } if order.waiter else None,
        "table": {
            "id": order.table.id,
            "table_number": order.table.table_number,
            "capacity": order.table.capacity,
            "status": order.table.status,
            "name": order.table.name,
            "notes": order.table.notes
        } if order.table else None
    }
    
    return order_dict


@router.put("/{order_id}")
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
    if order.status == "servido":
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
    
    # Cargar relaciones y convertir a diccionario
    order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.waiter),
        joinedload(Order.table)
    ).filter(Order.id == order_id).first()
    
    order_dict = {
        "id": order.id,
        "order_number": order.order_number,
        "table_id": order.table_id,
        "waiter_id": order.waiter_id,
        "sale_id": order.sale_id,
        "people_count": order.people_count,
        "status": order.status,
        "priority": order.priority,
        "notes": order.notes,
        "kitchen_notes": order.kitchen_notes,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "kitchen_start_time": order.kitchen_start_time,
        "kitchen_end_time": order.kitchen_end_time,
        "served_time": order.served_time,
        "items": [
            {
                "id": item.id,
                "order_id": item.order_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price) if item.unit_price else None,
                "subtotal": float(item.subtotal) if item.subtotal else None,
                "total": float(item.total) if item.total else None,
                "status": item.status,
                "special_instructions": item.special_instructions,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
                "kitchen_start_time": item.kitchen_start_time,
                "kitchen_end_time": item.kitchen_end_time,
                "product": {
                    "id": item.product.id,
                    "code": item.product.code,
                    "name": item.product.name,
                    "description": item.product.description,
                    "price": float(item.product.price) if item.product.price else None
                } if item.product else None
            }
            for item in order.items
        ],
        "waiter": {
            "id": order.waiter.id,
            "username": order.waiter.username,
            "email": order.waiter.email,
            "full_name": order.waiter.full_name,
            "role": order.waiter.role
        } if order.waiter else None,
        "table": {
            "id": order.table.id,
            "table_number": order.table.table_number,
            "capacity": order.table.capacity,
            "status": order.table.status,
            "name": order.table.name,
            "notes": order.table.notes
        } if order.table else None
    }
    
    return order_dict


@router.post("/{order_id}/add-items")
def add_items_to_order(
    order_id: int,
    items_data: List[OrderItemCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Agregar items a una orden existente"""
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
    if order.status == "servido":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una orden ya servida"
        )
    
    # No se puede modificar orden cancelada
    if order.status == "cancelado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una orden cancelada"
        )
    
    try:
        # Agregar cada item
        for item_data in items_data:
            # Verificar que el producto existe
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con ID {item_data.product_id} no encontrado"
                )
            
            # Verificar stock
            if product.stock < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para {product.name}. Disponible: {product.stock}"
                )
            
            # Usar precio del producto si no se especifica
            unit_price = item_data.unit_price or product.price
            subtotal = unit_price * item_data.quantity
            
            # Crear el item
            order_item = OrderItem(
                order_id=order_id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=unit_price,
                subtotal=subtotal,
                special_instructions=item_data.special_instructions,
                status="pendiente"
            )
            
            db.add(order_item)
            
            # Actualizar stock del producto
            product.stock -= item_data.quantity
        
        # Si la orden estaba en preparación o lista, volverla a pendiente
        if order.status in ["en_preparacion", "listo"]:
            order.status = "pendiente"
            order.kitchen_start_time = None
            order.kitchen_end_time = None
        
        db.commit()
        db.refresh(order)
        
        return order
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar items: {str(e)}"
        )


@router.delete("/{order_id}/items/{item_id}")
def remove_item_from_order(
    order_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar un item específico de una orden"""
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
    if order.status == "servido":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una orden ya servida"
        )
    
    # Buscar el item
    order_item = db.query(OrderItem).filter(
        OrderItem.id == item_id,
        OrderItem.order_id == order_id
    ).first()
    
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado en esta orden"
        )
    
    try:
        # Restaurar stock del producto
        product = db.query(Product).filter(Product.id == order_item.product_id).first()
        if product:
            product.stock += order_item.quantity
        
        # Eliminar el item
        db.delete(order_item)
        
        # Si la orden estaba en preparación o lista, volverla a pendiente
        if order.status in ["en_preparacion", "listo"]:
            order.status = "pendiente"
            order.kitchen_start_time = None
            order.kitchen_end_time = None
        
        db.commit()
        
        return {"message": "Item eliminado exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar item: {str(e)}"
        )


@router.post("/{order_id}/complete-payment")
def complete_order_payment(
    order_id: int,
    payment_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Completar el pago de una orden servida"""
    # Verificar que el usuario sea mesero o admin
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los meseros pueden completar pagos"
        )
    
    # Obtener la orden
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    # Verificar que la orden esté servida
    if order.status != "servido":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede completar el pago de órdenes servidas"
        )
    
    # Verificar que la orden tenga una venta asociada
    if not order.sale_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La orden no tiene una venta asociada"
        )
    
    # Obtener la venta
    sale = db.query(Sale).filter(Sale.id == order.sale_id).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    
    # Actualizar el estado de la venta a completada
    sale.status = "completada"
    sale.completed_at = datetime.now()
    
    # Si se proporciona información de pago, crear el método de pago
    if payment_data.get("payment_method"):
        from app.models.sale import PaymentMethod
        
        payment_method = PaymentMethod(
            sale_id=sale.id,
            payment_type=payment_data["payment_method"],
            amount=sale.total,
            reference=payment_data.get("reference"),
            notes=payment_data.get("notes", f"Pago completado por {current_user.full_name}")
        )
        db.add(payment_method)
    
    db.commit()
    db.refresh(sale)
    
    return {
        "message": "Pago completado exitosamente",
        "sale_id": sale.id,
        "sale_number": sale.sale_number,
        "total": float(sale.total),
        "completed_at": sale.completed_at
    }


@router.get("/{order_id}/sale-info")
def get_order_sale_info(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener información de la venta asociada a una orden"""
    # Obtener la orden
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
    
    # Si no hay venta asociada
    if not order.sale_id:
        return {
            "has_sale": False,
            "message": "La orden aún no tiene una venta asociada"
        }
    
    # Obtener la venta con sus items
    sale = db.query(Sale).options(
        joinedload(Sale.items)
    ).filter(Sale.id == order.sale_id).first()
    
    if not sale:
        return {
            "has_sale": False,
            "message": "Venta no encontrada"
        }
    
    return {
        "has_sale": True,
        "sale": {
            "id": sale.id,
            "sale_number": sale.sale_number,
            "total": float(sale.total),
            "status": sale.status,
            "created_at": sale.created_at,
            "completed_at": sale.completed_at,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "total": float(item.total)
                }
                for item in sale.items
            ]
        }
    }


@router.post("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancelar una orden"""
    # Verificar que el usuario sea mesero o admin
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los meseros pueden cancelar órdenes"
        )
    
    # Obtener la orden
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
            detail="No tienes permiso para cancelar esta orden"
        )
    
    # Verificar que la orden no esté ya servida
    if order.status == "servido":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar una orden ya servida"
        )
    
    # Verificar que la orden no esté ya cancelada
    if order.status == "cancelado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La orden ya está cancelada"
        )
    
    try:
        # Restaurar stock de todos los items
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
        
        # Cambiar estado a cancelado
        order.status = "cancelado"
        
        db.commit()
        
        return {"message": "Orden cancelada exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelando orden: {str(e)}"
        )


@router.post("/{order_id}/duplicate", response_model=OrderResponse)
def duplicate_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duplicar una orden existente"""
    # Verificar que el usuario sea mesero
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los meseros pueden duplicar órdenes"
        )
    
    # Obtener la orden original
    original_order = db.query(Order).filter(Order.id == order_id).first()
    if not original_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.MESERO and original_order.waiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para duplicar esta orden"
        )
    
    try:
        # Crear nueva orden
        new_order_number = generate_order_number(db)
        new_order = Order(
            order_number=new_order_number,
            table_id=original_order.table_id,
            waiter_id=current_user.id,
            people_count=original_order.people_count,
            priority=original_order.priority,
            notes=f"Duplicada de orden {original_order.order_number}",
            status="pendiente"
        )
        
        db.add(new_order)
        db.flush()  # Para obtener el ID de la nueva orden
        
        # Duplicar items
        for original_item in original_order.items:
            # Verificar stock
            product = db.query(Product).filter(Product.id == original_item.product_id).first()
            if product and product.stock >= original_item.quantity:
                new_item = OrderItem(
                    order_id=new_order.id,
                    product_id=original_item.product_id,
                    quantity=original_item.quantity,
                    unit_price=original_item.unit_price,
                    subtotal=original_item.subtotal,
                    special_instructions=original_item.special_instructions,
                    status="pendiente"
                )
                db.add(new_item)
                
                # Actualizar stock
                product.stock -= original_item.quantity
        
        db.commit()
        db.refresh(new_order)
        
        return new_order
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error duplicando orden: {str(e)}"
        )


@router.post("/{order_id}/add-items")
def add_items_to_order(
    order_id: int,
    items_data: List[OrderItemCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Agregar items a una orden existente"""
    # Verificar que el usuario sea mesero
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los meseros pueden agregar items a órdenes"
        )
    
    # Obtener la orden
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    # Verificar que la orden no esté completada o cancelada
    if order.status in ["servido", "cancelado"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden agregar items a una orden completada o cancelada"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.MESERO and order.waiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar esta orden"
        )
    
    try:
        for item_data in items_data:
            # Verificar que el producto existe
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto {item_data.product_id} no encontrado"
                )
            
            # Verificar stock
            if product.stock < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para {product.name}"
                )
            
            # Crear el item
            order_item = OrderItem(
                order_id=order_id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=product.price,
                subtotal=product.price * item_data.quantity,
                status="pendiente"
            )
            
            db.add(order_item)
            
            # Actualizar stock
            product.stock -= item_data.quantity
        
        db.commit()
        
        return {"message": "Items agregados exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error agregando items: {str(e)}"
        )


@router.post("/{order_id}/convert-to-sale")
def convert_order_to_sale(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Convertir una orden completada en una venta"""
    # Verificar que el usuario sea mesero
    if current_user.role not in [UserRole.MESERO, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los meseros pueden convertir órdenes a ventas"
        )
    
    # Obtener la orden
    order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )
    
    # Verificar que la orden esté lista para ser servida
    if order.status != "listo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden convertir órdenes que estén listas"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.MESERO and order.waiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para convertir esta orden"
        )
    
    try:
        # Crear la venta
        sale_number = generate_sale_number(db)
        total_amount = sum(item.subtotal for item in order.items)
        
        sale = Sale(
            sale_number=sale_number,
            customer_id=None,  # Venta sin cliente específico
            waiter_id=order.waiter_id,
            table_id=order.table_id,
            total_amount=total_amount,
            payment_method="efectivo",  # Por defecto
            status=SaleStatus.COMPLETADA,
            notes=f"Convertida de orden {order.order_number}"
        )
        
        db.add(sale)
        db.flush()  # Para obtener el ID de la venta
        
        # Crear items de venta
        for order_item in order.items:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=order_item.product_id,
                quantity=order_item.quantity,
                unit_price=order_item.unit_price,
                subtotal=order_item.subtotal
            )
            db.add(sale_item)
        
        # Marcar orden como servida
        order.status = "servido"
        
        # Liberar la mesa
        if order.table:
            order.table.status = TableStatus.FREE
        
        db.commit()
        db.refresh(sale)
        
        return {
            "message": "Orden convertida a venta exitosamente",
            "sale_number": sale.sale_number,
            "total_amount": float(sale.total_amount),
            "sale_id": sale.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error convirtiendo orden a venta: {str(e)}"
        )
