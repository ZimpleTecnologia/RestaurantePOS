"""
Esquemas Pydantic para el sistema de Gestión de Menús unificado
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


# Esquemas para Plato
class PlatoBase(BaseModel):
    """Schema base para plato"""
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: str = Field(..., min_length=1, max_length=20)
    tipo: str = Field(..., pattern=r'^(Fijo|Variable)$')
    categoria: Optional[str] = Field(None, max_length=50)
    activo: bool = True


class PlatoCreate(PlatoBase):
    """Schema para crear plato"""
    pass


class PlatoUpdate(BaseModel):
    """Schema para actualizar plato"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Optional[str] = Field(None, min_length=1, max_length=20)
    tipo: Optional[str] = Field(None, pattern=r'^(Fijo|Variable)$')
    categoria: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None


class PlatoResponse(PlatoBase):
    """Schema para respuesta de plato"""
    id: int
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


# Esquemas para Menu
class MenuBase(BaseModel):
    """Schema base para menú"""
    fecha: date
    activo: bool = True
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None


class MenuCreate(MenuBase):
    """Schema para crear menú"""
    platos_ids: List[int] = Field(..., min_items=1, description="Lista de IDs de platos")


class MenuUpdate(BaseModel):
    """Schema para actualizar menú"""
    activo: Optional[bool] = None
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    platos_ids: Optional[List[int]] = Field(None, min_items=1, description="Lista de IDs de platos")


class MenuResponse(MenuBase):
    """Schema para respuesta de menú"""
    id: int
    platos: List[PlatoResponse] = []
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class MenuDelDiaResponse(BaseModel):
    """Schema para menú del día con platos organizados"""
    menu: MenuResponse
    platos_fijos: List[PlatoResponse] = []
    platos_variables: List[PlatoResponse] = []
    platos_por_categoria: dict = {}


# Esquemas para respuestas de API
class MenuListResponse(BaseModel):
    """Schema para lista de menús"""
    menus: List[MenuResponse]
    total: int
    page: int
    size: int


class PlatoListResponse(BaseModel):
    """Schema para lista de platos"""
    platos: List[PlatoResponse]
    total: int
    page: int
    size: int
