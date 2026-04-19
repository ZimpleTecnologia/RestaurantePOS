"""
Esquemas Pydantic para Órdenes
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any
from datetime import datetime

# Definir tipos literales para validación
OrderStatusType = Literal["borrador", "pendiente", "confirmado", "preparando", "listo", "servido", "pagado", "cancelado"]
OrderPriorityType = Literal["baja", "normal", "alta", "urgente"]
ItemTypeLiteral = Literal["product", "menu", "plato"]


class OrderItemOptionBase(BaseModel):
    """Esquema base para opciones de item de orden (acompañamientos, etc)"""
    categoria: str
    opcion_elegida: str
    opcion_plato_id: Optional[int] = None


class OrderItemBase(BaseModel):
    """Esquema base para items de orden"""
    item_type: ItemTypeLiteral = "product"
    product_id: Optional[int] = None
    menu_id: Optional[int] = None
    plato_id: Optional[int] = None
    quantity: int = 1
    unit_price: Optional[float] = None
    notes: Optional[str] = None
    special_instructions: Optional[str] = None
    opciones: Optional[List[OrderItemOptionBase]] = []


class OrderItemCreate(OrderItemBase):
    """Esquema para crear item de orden"""
    pass


class OrderItemResponse(OrderItemBase):
    """Esquema de respuesta para item de orden"""
    id: int
    order_id: int
    total_price: float
    is_ready: bool = False
    is_served: bool = False
    snapshot_name: Optional[str] = None
    snapshot_description: Optional[str] = None
    snapshot_price: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Esquema base para órdenes"""
    table_id: int
    waiter_id: Optional[int] = None
    order_type: str = "mesa" # mesa, para_llevar, domicilio
    source: str = "pos" # pos, app, etc
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Esquema para crear orden"""
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    """Esquema para actualizar orden"""
    status: Optional[OrderStatusType] = None
    notes: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = None


class OrderResponse(OrderBase):
    """Esquema de respuesta para orden"""
    id: int
    order_number: str
    status: OrderStatusType
    total_amount: float
    tax_amount: float
    final_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Información extendida
    table_name: Optional[str] = None
    waiter_name: Optional[str] = None
    
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class KitchenOrderResponse(BaseModel):
    """Esquema para vista de cocina"""
    id: int
    order_number: str
    table_name: Optional[str] = None
    waiter_name: Optional[str] = None
    status: str
    created_at: datetime
    hora_envio: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

class OrderStatsResponse(BaseModel):
    """Estadísticas de órdenes"""
    total: int
    pendientes: int
    en_preparacion: int
    listos: int
    confirmados: int
    pedidos_hoy: int
