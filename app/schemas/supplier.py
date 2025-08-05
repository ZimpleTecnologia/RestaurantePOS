"""
Esquemas Pydantic para Proveedores y Compras
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.supplier import PurchaseStatus


class SupplierBase(BaseModel):
    """Esquema base para proveedores"""
    name: str
    document_type: str
    document_number: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    credit_limit: Decimal = 0
    payment_terms: Optional[str] = None
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    """Esquema para crear proveedor"""
    pass


class SupplierUpdate(BaseModel):
    """Esquema para actualizar proveedor"""
    name: Optional[str] = None
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class SupplierResponse(SupplierBase):
    """Esquema de respuesta para proveedor"""
    id: int
    current_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PurchaseItemBase(BaseModel):
    """Esquema base para items de compra"""
    product_id: int
    quantity: int
    unit_cost: Decimal
    discount: Decimal = 0
    received_quantity: int = 0
    lot_number: Optional[str] = None
    expiration_date: Optional[datetime] = None
    notes: Optional[str] = None


class PurchaseItemCreate(PurchaseItemBase):
    """Esquema para crear item de compra"""
    pass


class PurchaseItemResponse(PurchaseItemBase):
    """Esquema de respuesta para item de compra"""
    id: int
    total: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


class PurchaseBase(BaseModel):
    """Esquema base para compras"""
    supplier_id: int
    subtotal: Decimal = 0
    tax: Decimal = 0
    discount: Decimal = 0
    total: Decimal = 0
    status: PurchaseStatus = PurchaseStatus.PENDIENTE
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    expected_delivery: Optional[datetime] = None
    notes: Optional[str] = None


class PurchaseCreate(PurchaseBase):
    """Esquema para crear compra"""
    items: List[PurchaseItemCreate]


class PurchaseUpdate(BaseModel):
    """Esquema para actualizar compra"""
    supplier_id: Optional[int] = None
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    total: Optional[Decimal] = None
    status: Optional[PurchaseStatus] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    expected_delivery: Optional[datetime] = None
    notes: Optional[str] = None


class PurchaseResponse(PurchaseBase):
    """Esquema de respuesta para compra"""
    id: int
    purchase_number: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    items: List[PurchaseItemResponse] = []
    
    class Config:
        from_attributes = True


class PurchaseWithDetails(PurchaseResponse):
    """Esquema de compra con detalles completos"""
    supplier_name: str
    user_name: str 