"""
Schemas Pydantic para el módulo de Pedidos a Cocina
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ===== SCHEMAS BASE =====

class PedidoMenuOpcionBase(BaseModel):
    """Schema base para opciones de menú"""
    categoria: str = Field(..., description="Categoría de la opción (ej: 'Proteína')")
    opcion_elegida: str = Field(..., description="Nombre de la opción elegida")
    opcion_plato_id: Optional[int] = Field(None, description="ID del plato elegido")


class PedidoDetalleBase(BaseModel):
    """Schema base para detalle de pedido"""
    tipo_item: str = Field(..., description="Tipo de item: 'MENU' o 'PLATO'")
    menu_id: Optional[int] = Field(None, description="ID del menú del día (si aplica)")
    plato_id: Optional[int] = Field(None, description="ID del plato especial (si aplica)")
    observaciones: Optional[str] = Field(None, description="Observaciones del item")
    opciones_menu: Optional[List[PedidoMenuOpcionBase]] = Field([], description="Opciones elegidas para el menú")


class PedidoCocinaBase(BaseModel):
    """Schema base para pedido a cocina"""
    mesa_id: int = Field(..., description="ID de la mesa")
    observaciones: Optional[str] = Field(None, description="Observaciones generales del pedido")


# ===== SCHEMAS PARA CREACIÓN =====

class PedidoMenuOpcionCreate(PedidoMenuOpcionBase):
    """Schema para crear opción de menú"""
    pass


class PedidoDetalleCreate(PedidoDetalleBase):
    """Schema para crear detalle de pedido"""
    pass


class PedidoCocinaCreate(PedidoCocinaBase):
    """Schema para crear pedido a cocina"""
    detalles: Optional[List[PedidoDetalleCreate]] = Field([], description="Detalles del pedido")


# ===== SCHEMAS DE RESPUESTA =====

class PedidoMenuOpcionResponse(PedidoMenuOpcionBase):
    """Schema de respuesta para opción de menú"""
    id: int
    pedido_detalle_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PedidoDetalleResponse(BaseModel):
    """Schema de respuesta para detalle de pedido"""
    id: int
    pedido_id: int
    tipo_item: str
    menu_id: Optional[int]
    plato_id: Optional[int]
    nombre_snapshot: str
    descripcion_snapshot: Optional[str]
    precio_snapshot: Optional[Decimal]
    observaciones: Optional[str]
    created_at: datetime
    opciones: List[PedidoMenuOpcionResponse] = []
    
    class Config:
        from_attributes = True


class PedidoCocinaResponse(BaseModel):
    """Schema de respuesta para pedido a cocina"""
    id: int
    mesa_id: int
    mesero_id: int
    estado: str
    observaciones: Optional[str]
    fecha: datetime
    hora_envio: Optional[datetime]
    hora_inicio_preparacion: Optional[datetime]
    hora_finalizacion: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Información relacionada
    mesa_nombre: Optional[str] = None
    mesa_numero: Optional[int] = None
    mesero_nombre: Optional[str] = None
    tiempo_transcurrido: Optional[str] = None  # Para KDS
    
    detalles: List[PedidoDetalleResponse] = []
    
    class Config:
        from_attributes = True


class PedidoCocinaListResponse(BaseModel):
    """Schema para lista de pedidos"""
    pedidos: List[PedidoCocinaResponse]
    total: int


# ===== SCHEMAS PARA ACTUALIZACIÓN =====

class PedidoCocinaUpdate(BaseModel):
    """Schema para actualizar pedido (solo cuando está en BORRADOR)"""
    observaciones: Optional[str] = None
    detalles: Optional[List[PedidoDetalleCreate]] = None


class CambiarEstadoPedido(BaseModel):
    """Schema para cambiar estado del pedido (desde cocina)"""
    estado: str = Field(..., description="Nuevo estado: 'PENDIENTE', 'EN_PREPARACION', 'LISTO'")

