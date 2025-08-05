"""
Esquemas Pydantic para Ventas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.sale import SaleStatus, PaymentMethodType


class SaleItemBase(BaseModel):
    """Esquema base para items de venta"""
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal = 0
    notes: Optional[str] = None


class SaleItemCreate(SaleItemBase):
    """Esquema para crear item de venta"""
    pass


class SaleItemResponse(SaleItemBase):
    """Esquema de respuesta para item de venta"""
    id: int
    total: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentMethodBase(BaseModel):
    """Esquema base para método de pago"""
    payment_type: PaymentMethodType
    amount: Decimal
    reference: Optional[str] = None
    notes: Optional[str] = None


class PaymentMethodCreate(PaymentMethodBase):
    """Esquema para crear método de pago"""
    pass


class PaymentMethodResponse(PaymentMethodBase):
    """Esquema de respuesta para método de pago"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    """Esquema base para ventas"""
    customer_id: Optional[int] = None
    location_id: Optional[int] = None
    table_id: Optional[int] = None
    subtotal: Decimal = 0
    tax: Decimal = 0
    discount: Decimal = 0
    total: Decimal = 0
    tip: Decimal = 0
    commission: Decimal = 0
    status: SaleStatus = SaleStatus.PENDIENTE
    notes: Optional[str] = None
    is_delivery: bool = False
    delivery_address: Optional[str] = None
    delivery_fee: Decimal = 0


class SaleCreate(SaleBase):
    """Esquema para crear venta"""
    items: List[SaleItemCreate]
    payments: List[PaymentMethodCreate]


class SaleUpdate(BaseModel):
    """Esquema para actualizar venta"""
    customer_id: Optional[int] = None
    location_id: Optional[int] = None
    table_id: Optional[int] = None
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    total: Optional[Decimal] = None
    tip: Optional[Decimal] = None
    commission: Optional[Decimal] = None
    status: Optional[SaleStatus] = None
    notes: Optional[str] = None
    is_delivery: Optional[bool] = None
    delivery_address: Optional[str] = None
    delivery_fee: Optional[Decimal] = None


class SaleResponse(SaleBase):
    """Esquema de respuesta para venta"""
    id: int
    sale_number: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    items: List[SaleItemResponse] = []
    payments: List[PaymentMethodResponse] = []
    
    class Config:
        from_attributes = True


class SaleWithDetails(SaleResponse):
    """Esquema de venta con detalles completos"""
    customer_name: Optional[str] = None
    user_name: str
    location_name: Optional[str] = None
    table_number: Optional[str] = None 