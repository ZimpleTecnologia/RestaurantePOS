"""
Schemas Pydantic para Mesa
Validación y serialización de datos para el módulo de Mesas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class MesaBase(BaseModel):
    """Schema base para Mesa"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre descriptivo de la mesa")
    numero: int = Field(..., gt=0, description="Número de la mesa (debe ser único)")
    capacidad: Optional[int] = Field(None, gt=0, le=50, description="Capacidad máxima de personas")
    estado: bool = Field(True, description="Estado de la mesa (True=Activo, False=Inactivo)")
    
    @validator('nombre')
    def validate_nombre(cls, v):
        """Valida que el nombre no esté vacío"""
        if not v or not v.strip():
            raise ValueError('El nombre de la mesa no puede estar vacío')
        return v.strip()
    
    @validator('numero')
    def validate_numero(cls, v):
        """Valida que el número sea positivo"""
        if v <= 0:
            raise ValueError('El número de mesa debe ser mayor que 0')
        return v


class MesaCreate(MesaBase):
    """Schema para crear una mesa"""
    pass


class MesaUpdate(BaseModel):
    """Schema para actualizar una mesa (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    numero: Optional[int] = Field(None, gt=0)
    capacidad: Optional[int] = Field(None, gt=0, le=50)
    estado: Optional[bool] = None
    
    @validator('nombre')
    def validate_nombre(cls, v):
        """Valida que el nombre no esté vacío si se proporciona"""
        if v is not None and (not v or not v.strip()):
            raise ValueError('El nombre de la mesa no puede estar vacío')
        return v.strip() if v else v


class MesaResponse(MesaBase):
    """Schema para respuesta de Mesa"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class MesaListResponse(BaseModel):
    """Schema para lista de mesas"""
    mesas: list[MesaResponse]
    total: int
    
    class Config:
        from_attributes = True


class MesaActivarDesactivar(BaseModel):
    """Schema para activar/desactivar mesa"""
    estado: bool = Field(..., description="Nuevo estado de la mesa")

