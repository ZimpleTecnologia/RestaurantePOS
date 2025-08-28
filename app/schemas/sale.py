"""
Esquemas Pydantic para Ventas - Simplificados
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from typing import Literal


class SaleItemCreate(BaseModel):
    """Esquema para crear item de venta"""
    product_id: int
    quantity: int
    price: Decimal


class SaleCreate(BaseModel):
    """Esquema para crear venta"""
    customer_id: Optional[int] = None
    items: List[SaleItemCreate]
    total: Decimal


class SaleUpdate(BaseModel):
    """Esquema para actualizar venta"""
    customer_id: Optional[int] = None
    total: Optional[Decimal] = None


class SaleItemResponse(BaseModel):
    """Esquema de respuesta para item de venta"""
    id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total: Decimal
    
    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    """Esquema de respuesta para venta"""
    id: int
    sale_number: str
    customer_id: Optional[int]
    user_id: int
    total: Decimal
    status: Literal["pendiente", "completada", "cancelada", "devuelta"]
    
    class Config:
        from_attributes = True


class SaleWithDetails(SaleResponse):
    """Esquema de venta con detalles"""
    items: List[SaleItemResponse] = []
    customer_name: Optional[str] = None
    
    class Config:
        from_attributes = True 