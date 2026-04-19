"""
Schemas para el sistema de Carta Restaurante

DEPRECATED: Usar schemas de restaurant_menu en su lugar
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TipoPlato(str, Enum):
    """Tipos de platos en la carta"""
    FIJO = "Fijo"
    VARIABLE = "Variable"


class CategoriaPlato(str, Enum):
    """Categorías de platos"""
    ENTRADA = "Entrada"
    PLATO_PRINCIPAL = "Plato Principal"
    ACOMPANAMIENTO = "Acompañamiento"
    BEBIDA = "Bebida"
    POSTRE = "Postre"
    OTRO = "Otro"


# ==================== SCHEMAS PARA CARTA RESTAURANTE ====================

class CartaRestauranteBase(BaseModel):
    """Schema base para platos de la carta"""
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio_base: Decimal = Field(..., ge=0)
    tipo: TipoPlato
    activo: bool = True
    categoria: Optional[str] = None


class CartaRestauranteCreate(CartaRestauranteBase):
    """Schema para crear un plato"""
    pass


class CartaRestauranteUpdate(BaseModel):
    """Schema para actualizar un plato"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = Field(None, ge=0)
    tipo: Optional[TipoPlato] = None
    activo: Optional[bool] = None
    categoria: Optional[str] = None


class CartaRestauranteResponse(CartaRestauranteBase):
    """Schema para respuesta de plato"""
    producto_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== SCHEMAS PARA MENÚ DEL DÍA ====================

class MenuDiaBase(BaseModel):
    """Schema base para menú del día"""
    fecha: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    nombre: str = Field(..., min_length=1, max_length=100)
    precio: Decimal = Field(..., ge=0)
    descripcion: Optional[str] = None
    activo: bool = True


class MenuDiaCreate(MenuDiaBase):
    """Schema para crear menú del día"""
    platos_fijos: List[int] = Field(default=[], description="IDs de platos fijos a incluir")
    platos_variables: List[int] = Field(default=[], description="IDs de platos variables a incluir")


class MenuDiaUpdate(BaseModel):
    """Schema para actualizar menú del día"""
    fecha: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    precio: Optional[Decimal] = Field(None, ge=0)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    platos_fijos: Optional[List[int]] = None
    platos_variables: Optional[List[int]] = None


class MenuDiaResponse(MenuDiaBase):
    """Schema para respuesta de menú del día"""
    menu_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    platos_fijos: List[CartaRestauranteResponse] = []
    platos_variables: List[CartaRestauranteResponse] = []
    
    class Config:
        from_attributes = True


# ==================== SCHEMAS PARA OPCIONES DEL MENÚ ====================

class MenuOpcionBase(BaseModel):
    """Schema base para opción del menú"""
    menu_id: int
    producto_id: int
    es_fijo: bool
    orden: int = 0


class MenuOpcionCreate(MenuOpcionBase):
    """Schema para crear opción del menú"""
    pass


class MenuOpcionResponse(MenuOpcionBase):
    """Schema para respuesta de opción del menú"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    producto: CartaRestauranteResponse
    
    class Config:
        from_attributes = True


# ==================== SCHEMAS PARA PEDIDOS ====================

class PedidoMenuBase(BaseModel):
    """Schema base para pedido de menú"""
    menu_id: int
    observaciones: Optional[str] = None


class PedidoMenuCreate(PedidoMenuBase):
    """Schema para crear pedido de menú"""
    opciones_elegidas: List[int] = Field(..., description="IDs de platos variables elegidos")


class PedidoMenuResponse(PedidoMenuBase):
    """Schema para respuesta de pedido de menú"""
    id: int
    menu: MenuDiaResponse
    opciones_elegidas: List[CartaRestauranteResponse] = []
    
    class Config:
        from_attributes = True


# ==================== SCHEMAS PARA ESTADÍSTICAS ====================

class CartaStatsResponse(BaseModel):
    """Schema para estadísticas de la carta"""
    total_platos: int
    platos_fijos: int
    platos_variables: int
    platos_activos: int
    platos_inactivos: int
    platos_por_categoria: dict


class MenuStatsResponse(BaseModel):
    """Schema para estadísticas de menús"""
    total_menus: int
    menus_activos: int
    menus_inactivos: int
    menu_hoy: Optional[MenuDiaResponse] = None


# ==================== SCHEMAS PARA CONSULTAS ====================

class MenuHoyResponse(BaseModel):
    """Schema para menú del día actual"""
    menu: Optional[MenuDiaResponse] = None
    platos_fijos: List[CartaRestauranteResponse] = []
    platos_variables_por_categoria: dict = {}


class CartaFiltros(BaseModel):
    """Schema para filtros de carta"""
    tipo: Optional[TipoPlato] = None
    categoria: Optional[str] = None
    activo: Optional[bool] = None
    search: Optional[str] = None
