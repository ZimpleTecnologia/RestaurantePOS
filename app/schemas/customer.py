"""
Esquemas Pydantic para Clientes y Créditos
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class CustomerBase(BaseModel):
    """Esquema base para clientes"""
    document_type: str
    document_number: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    credit_limit: Decimal = 0
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Esquema para crear cliente"""
    pass


class CustomerUpdate(BaseModel):
    """Esquema para actualizar cliente"""
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Esquema de respuesta para cliente"""
    id: int
    current_balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreditBase(BaseModel):
    """Esquema base para créditos"""
    customer_id: int
    sale_id: int
    amount: Decimal
    balance: Decimal
    due_date: Optional[date] = None
    interest_rate: float = 0
    notes: Optional[str] = None


class CreditCreate(CreditBase):
    """Esquema para crear crédito"""
    pass


class CreditUpdate(BaseModel):
    """Esquema para actualizar crédito"""
    amount: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    due_date: Optional[date] = None
    interest_rate: Optional[float] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CreditResponse(CreditBase):
    """Esquema de respuesta para crédito"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    """Esquema base para pagos"""
    customer_id: int
    credit_id: Optional[int] = None
    amount: Decimal
    payment_method: str
    reference: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Esquema para crear pago"""
    pass


class PaymentResponse(PaymentBase):
    """Esquema de respuesta para pago"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 