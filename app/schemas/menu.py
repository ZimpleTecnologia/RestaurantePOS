"""
Schemas para el sistema de menú del día
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.menu import MenuStatus


class CategoriaMenuBase(BaseModel):
    """Schema base para categorías del menú"""
    nombre: str = Field(..., max_length=50)
    orden: int = Field(default=0)
    descripcion: Optional[str] = None
    is_active: bool = Field(default=True)


class CategoriaMenuCreate(CategoriaMenuBase):
    """Schema para crear categorías del menú"""
    pass


class CategoriaMenuResponse(CategoriaMenuBase):
    """Schema de respuesta para categorías del menú"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OpcionMenuBase(BaseModel):
    """Schema base para opciones del menú"""
    nombre: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    is_active: bool = Field(default=True)


class OpcionMenuCreate(OpcionMenuBase):
    """Schema para crear opciones del menú"""
    categoria_id: int


class OpcionMenuResponse(OpcionMenuBase):
    """Schema de respuesta para opciones del menú"""
    id: int
    menu_id: int
    categoria_id: int
    categoria: CategoriaMenuResponse
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MenuDayBase(BaseModel):
    """Schema base para menú del día"""
    fecha: date
    nombre: str = Field(..., max_length=100)
    precio: Decimal = Field(..., decimal_places=2)
    descripcion: Optional[str] = None
    estado: MenuStatus = Field(default=MenuStatus.ACTIVE)


class MenuDayCreate(MenuDayBase):
    """Schema para crear menú del día"""
    opciones: List[OpcionMenuCreate] = Field(default=[])


class MenuDayResponse(MenuDayBase):
    """Schema de respuesta para menú del día"""
    id: int
    opciones: List[OpcionMenuResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MenuDayWithCategories(MenuDayResponse):
    """Schema de respuesta para menú del día con opciones agrupadas por categoría"""
    opciones_por_categoria: dict = Field(default={})


class MenuItemCreate(BaseModel):
    """Schema para crear items de menú en un pedido"""
    menu_id: int
    categoria_id: int
    opcion_id: int
    quantity: int = Field(default=1, ge=1)
    observaciones: Optional[str] = None


class MenuItemResponse(BaseModel):
    """Schema de respuesta para items de menú en un pedido"""
    id: int
    menu_id: int
    categoria_id: int
    opcion_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    observaciones: Optional[str] = None
    menu: MenuDayResponse
    categoria: CategoriaMenuResponse
    opcion: OpcionMenuResponse

    class Config:
        from_attributes = True


class OrderWithMenuItems(BaseModel):
    """Schema para pedido con items de menú"""
    id: int
    order_number: str
    table_id: Optional[int] = None
    waiter_id: int
    status: str
    estado_cocina: str
    total_amount: Decimal
    final_amount: Decimal
    created_at: datetime
    menu_items: List[MenuItemResponse] = []

    class Config:
        from_attributes = True


