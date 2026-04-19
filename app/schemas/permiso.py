"""
Schemas Pydantic para Permisos
Validación y serialización de datos para el módulo de Permisos
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class PermisoBase(BaseModel):
    """Schema base para Permiso"""
    codigo: str = Field(..., min_length=2, max_length=50, description="Código único del permiso")
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre descriptivo del permiso")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción del permiso")
    modulo: str = Field(..., min_length=2, max_length=50, description="Módulo al que pertenece")
    estado: bool = Field(True, description="Estado del permiso")
    
    @validator('codigo')
    def validate_codigo(cls, v):
        """Valida formato del código (solo letras minúsculas, números y guiones bajos)"""
        if not v or not v.strip():
            raise ValueError('El código no puede estar vacío')
        codigo = v.strip().lower()
        if not codigo.replace('_', '').replace('-', '').isalnum():
            raise ValueError('El código solo puede contener letras, números, guiones y guiones bajos')
        return codigo
    
    @validator('nombre')
    def validate_nombre(cls, v):
        """Valida que el nombre no esté vacío"""
        if not v or not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()
    
    @validator('modulo')
    def validate_modulo(cls, v):
        """Valida que el módulo no esté vacío"""
        if not v or not v.strip():
            raise ValueError('El módulo no puede estar vacío')
        return v.strip().lower()


class PermisoCreate(PermisoBase):
    """Schema para crear un permiso"""
    pass


class PermisoUpdate(BaseModel):
    """Schema para actualizar un permiso"""
    codigo: Optional[str] = Field(None, min_length=2, max_length=50)
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    modulo: Optional[str] = Field(None, min_length=2, max_length=50)
    estado: Optional[bool] = None
    
    @validator('codigo')
    def validate_codigo(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El código no puede estar vacío')
            codigo = v.strip().lower()
            if not codigo.replace('_', '').replace('-', '').isalnum():
                raise ValueError('El código solo puede contener letras, números, guiones y guiones bajos')
            return codigo
        return v


class PermisoResponse(PermisoBase):
    """Schema para respuesta de Permiso"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class PermisoListResponse(BaseModel):
    """Schema para lista de permisos"""
    permisos: List[PermisoResponse]
    total: int
    
    class Config:
        from_attributes = True


class PermisoSimple(BaseModel):
    """Schema simple de permiso (para relaciones)"""
    id: int
    codigo: str
    nombre: str
    modulo: str
    
    class Config:
        from_attributes = True


class AsignarPermisoRequest(BaseModel):
    """Schema para asignar permisos a un usuario"""
    permiso_ids: List[int] = Field(..., description="Lista de IDs de permisos a asignar")
    
    @validator('permiso_ids')
    def validate_permiso_ids(cls, v):
        if not v:
            raise ValueError('Debe proporcionar al menos un permiso')
        if len(v) != len(set(v)):
            raise ValueError('No se pueden asignar permisos duplicados')
        return v


class RemoverPermisoRequest(BaseModel):
    """Schema para remover un permiso de un usuario"""
    permiso_id: int = Field(..., gt=0, description="ID del permiso a remover")

