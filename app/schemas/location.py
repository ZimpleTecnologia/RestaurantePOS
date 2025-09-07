"""
Esquemas Pydantic para Ubicaciones y Mesas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.location import LocationType, TableStatus


class LocationBase(BaseModel):
    """Esquema base para ubicaciones"""
    name: str
    description: Optional[str] = None
    location_type: LocationType = LocationType.RESTAURANTE
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_name: Optional[str] = None
    capacity: int = 0
    notes: Optional[str] = None


class LocationCreate(LocationBase):
    """Esquema para crear ubicación"""
    pass


class LocationUpdate(BaseModel):
    """Esquema para actualizar ubicación"""
    name: Optional[str] = None
    description: Optional[str] = None
    location_type: Optional[LocationType] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    manager_name: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class LocationResponse(LocationBase):
    """Esquema de respuesta para ubicación"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TableBase(BaseModel):
    """Esquema base para mesas"""
    location_id: Optional[int] = None
    table_number: str
    name: Optional[str] = None
    capacity: int = 4
    status: TableStatus = TableStatus.LIBRE
    notes: Optional[str] = None


class TableCreate(TableBase):
    """Esquema para crear mesa"""
    pass


class TableUpdate(BaseModel):
    """Esquema para actualizar mesa"""
    location_id: Optional[int] = None
    table_number: Optional[str] = None
    name: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[TableStatus] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class TableResponse(TableBase):
    """Esquema de respuesta para mesa"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    active_orders: Optional[int] = 0
    
    class Config:
        from_attributes = True


class TableWithLocation(TableResponse):
    """Esquema de mesa con información de ubicación"""
    location_name: str 