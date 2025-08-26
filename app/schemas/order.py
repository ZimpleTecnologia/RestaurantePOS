"""
Esquemas Pydantic para Órdenes
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any
from datetime import datetime

# Definir tipos literales para validación
OrderStatusType = Literal["pendiente", "en_preparacion", "listo", "servido", "cancelado"]
OrderPriorityType = Literal["baja", "normal", "alta", "urgente"]


class OrderItemBase(BaseModel):
    """Esquema base para items de orden"""
    product_id: int
    quantity: int
    unit_price: Optional[float] = None
    special_instructions: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    """Esquema para crear item de orden"""
    pass


class OrderItemUpdate(BaseModel):
    """Esquema para actualizar item de orden"""
    quantity: Optional[int] = None
    special_instructions: Optional[str] = None
    status: Optional[OrderStatusType] = None


class OrderItemResponse(OrderItemBase):
    """Esquema de respuesta para item de orden"""
    id: int
    order_id: int
    subtotal: float
    total: Optional[float] = None
    status: Optional[OrderStatusType] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    kitchen_start_time: Optional[datetime] = None
    kitchen_end_time: Optional[datetime] = None
    
    # Información del producto
    product: Optional[dict] = None
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Esquema base para órdenes"""
    table_id: int
    people_count: int = 1
    priority: OrderPriorityType = "normal"
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Esquema para crear orden"""
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    """Esquema para actualizar orden"""
    people_count: Optional[int] = None
    priority: Optional[OrderPriorityType] = None
    status: Optional[OrderStatusType] = None
    notes: Optional[str] = None
    kitchen_notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Esquema de respuesta para orden"""
    id: int
    order_number: str
    waiter_id: int
    sale_id: Optional[int] = None
    status: OrderStatusType
    created_at: datetime
    updated_at: Optional[datetime] = None
    kitchen_start_time: Optional[datetime] = None
    kitchen_end_time: Optional[datetime] = None
    served_time: Optional[datetime] = None
    
    # Relaciones
    items: List[OrderItemResponse] = []
    waiter: Optional[dict] = None
    table: Optional[dict] = None
    
    class Config:
        from_attributes = True


class KitchenOrderResponse(BaseModel):
    """Esquema de respuesta específico para la vista de cocina"""
    id: int
    order_number: str
    table_number: str
    waiter_name: str
    people_count: int
    status: OrderStatusType
    priority: OrderPriorityType
    created_at: datetime
    kitchen_start_time: Optional[datetime] = None
    kitchen_end_time: Optional[datetime] = None
    notes: Optional[str] = None
    kitchen_notes: Optional[str] = None
    
    # Items de la orden
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
