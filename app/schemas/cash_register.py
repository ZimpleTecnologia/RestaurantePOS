"""
Esquemas para el sistema de caja
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.cash_register import CASH_REGISTER_STATUS, CASH_MOVEMENT_TYPE


# Esquemas para CashRegister
class CashRegisterBase(BaseModel):
    register_number: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CashRegisterCreate(CashRegisterBase):
    pass


class CashRegisterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CashRegisterResponse(CashRegisterBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Esquemas para CashSession
class CashSessionBase(BaseModel):
    cash_register_id: int
    opening_amount: Decimal = Field(..., ge=0)
    opening_notes: Optional[str] = None


class CashSessionCreate(CashSessionBase):
    pass


class CashSessionClose(BaseModel):
    closing_amount: Decimal = Field(..., ge=0)
    closing_notes: Optional[str] = None


class CashSessionResponse(CashSessionBase):
    id: int
    user_id: int
    session_number: str
    opened_at: datetime
    closing_amount: Optional[Decimal] = None
    closing_notes: Optional[str] = None
    closed_at: Optional[datetime] = None
    status: str
    user_name: Optional[str] = None
    cash_register_name: Optional[str] = None

    class Config:
        from_attributes = True


# Esquemas para CashMovement
class CashMovementBase(BaseModel):
    movement_type: str
    amount: Decimal = Field(..., gt=0)
    description: str = Field(..., min_length=1)
    reference: Optional[str] = None
    notes: Optional[str] = None


class CashMovementCreate(CashMovementBase):
    session_id: int


class CashMovementResponse(CashMovementBase):
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Esquemas para reportes
class CashSessionSummary(BaseModel):
    session_id: int
    session_number: str
    opened_at: datetime
    closed_at: Optional[datetime] = None
    opening_amount: Decimal
    closing_amount: Optional[Decimal] = None
    total_sales: Decimal
    total_refunds: Decimal
    total_expenses: Decimal
    total_withdrawals: Decimal
    total_deposits: Decimal
    expected_amount: Decimal
    difference: Optional[Decimal] = None
    status: str
    user_name: str
    cash_register_name: str


class CashRegisterReport(BaseModel):
    cash_register_id: int
    cash_register_name: str
    total_sessions: int
    open_sessions: int
    closed_sessions: int
    total_amount: Decimal
    total_sales: Decimal
    total_expenses: Decimal
    period_start: datetime
    period_end: datetime
