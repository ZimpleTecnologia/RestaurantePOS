"""
Esquemas Pydantic para el sistema de menús del restaurante
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal
from enum import Enum


# Esquemas para CategoriaMenu
class CategoriaMenuBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    descripcion: Optional[str] = None
    orden: int = Field(default=0, ge=0)
    is_active: bool = True


class CategoriaMenuCreate(CategoriaMenuBase):
    pass


class CategoriaMenuUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion: Optional[str] = None
    orden: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CategoriaMenuResponse(CategoriaMenuBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Método personalizado para convertir desde ORM"""
        return cls(
            id=obj.id,
            nombre=obj.nombre,
            descripcion=obj.descripcion,
            orden=obj.orden,
            is_active=obj.is_active if obj.is_active is not None else True,
            created_at=str(obj.created_at) if obj.created_at else None,
            updated_at=str(obj.updated_at) if obj.updated_at else None
        )


# Esquemas para PlatoRestaurante
class PlatoRestauranteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Decimal = Field(..., ge=0)
    tipo: str = Field(..., pattern=r'^(Menu_Dia|Plato_Fijo|Acompanamiento_Fijo)$')
    activo: bool = True
    categoria_id: Optional[int] = None  # Categoría sugerida por defecto


class PlatoRestauranteCreate(PlatoRestauranteBase):
    pass


class PlatoRestauranteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = Field(None, ge=0)
    tipo: Optional[str] = Field(None, pattern=r'^(Menu_Dia|Plato_Fijo|Acompanamiento_Fijo)$')
    activo: Optional[bool] = None
    categoria_id: Optional[int] = None


class PlatoRestauranteResponse(PlatoRestauranteBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tiene_imagen: Optional[bool] = False
    imagen_data: Optional[bool] = False  # Solo indica si tiene imagen, no los datos
    categoria: Optional[Dict] = None  # Información de la categoría si existe
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Método personalizado para convertir desde ORM"""
        categoria_info = None
        if obj.categoria:
            categoria_info = {
                "id": obj.categoria.id,
                "nombre": obj.categoria.nombre
            }
        
        return cls(
            id=obj.id,
            nombre=obj.nombre,
            descripcion=obj.descripcion,
            precio=obj.precio,
            tipo=obj.tipo,
            activo=obj.activo if obj.activo is not None else True,
            categoria_id=obj.categoria_id,
            created_at=str(obj.created_at) if obj.created_at else None,
            updated_at=str(obj.updated_at) if obj.updated_at else None,
            tiene_imagen=obj.imagen_data is not None,
            imagen_data=obj.imagen_data is not None,
            categoria=categoria_info
        )


# Esquemas para AcompanamientoFijo
class AcompanamientoFijoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activo: bool = True
    orden: int = Field(default=0, ge=0)


class AcompanamientoFijoCreate(AcompanamientoFijoBase):
    pass


class AcompanamientoFijoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    orden: Optional[int] = Field(None, ge=0)


class AcompanamientoFijoResponse(AcompanamientoFijoBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Método personalizado para convertir desde ORM"""
        return cls(
            id=obj.id,
            nombre=obj.nombre,
            descripcion=obj.descripcion,
            activo=obj.activo if obj.activo is not None else True,
            orden=obj.orden,
            created_at=str(obj.created_at) if obj.created_at else None,
            updated_at=str(obj.updated_at) if obj.updated_at else None
        )


# Esquemas para MenuDia
class MenuDiaEstado(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"


class MenuDiaBase(BaseModel):
    fecha: date
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Decimal = Field(default=0, ge=0)
    estado: MenuDiaEstado = MenuDiaEstado.DRAFT


class MenuDiaCreate(MenuDiaBase):
    categorias_platos: Dict[str, List[int]] = Field(
        default_factory=dict,
        description="Diccionario con categorías y sus platos: {'Principio': [1,2], 'Proteína': [3,4]}"
    )


class MenuDiaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    precio: Optional[Decimal] = Field(None, ge=0)
    descripcion: Optional[str] = None
    estado: Optional[MenuDiaEstado] = None
    categorias_platos: Optional[Dict[str, List[int]]] = None


class MenuDiaResponse(MenuDiaBase):
    id: int
    categorias_platos: Dict[str, List['PlatoRestauranteResponse']] = Field(default_factory=dict)
    total_platos: int = 0
    activo: bool = False
    publicado: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Método personalizado para convertir desde ORM"""
        legacy_map = {
            "activo": MenuDiaEstado.ACTIVE,
            "inactivo": MenuDiaEstado.INACTIVE,
            "borrador": MenuDiaEstado.DRAFT
        }
        raw_estado = obj.estado if obj.estado else MenuDiaEstado.DRAFT.value
        estado_enum = legacy_map.get(str(raw_estado).lower())
        if not estado_enum:
            try:
                estado_enum = MenuDiaEstado(str(raw_estado).upper())
            except ValueError:
                estado_enum = MenuDiaEstado.DRAFT

        return cls(
            id=obj.id,
            fecha=obj.fecha,
            nombre=obj.nombre,
            precio=obj.precio,
            descripcion=obj.descripcion,
            estado=estado_enum,
            activo=estado_enum == MenuDiaEstado.ACTIVE,
            publicado=estado_enum == MenuDiaEstado.ACTIVE,
            created_at=str(obj.created_at) if obj.created_at else None,
            updated_at=str(obj.updated_at) if obj.updated_at else None
        )


# Esquemas para MenuCategoriaPlato
class MenuCategoriaPlatoBase(BaseModel):
    menu_dia_id: int
    categoria_id: int
    plato_id: int
    activo: bool = True


class MenuCategoriaPlatoCreate(MenuCategoriaPlatoBase):
    pass


class MenuCategoriaPlatoResponse(MenuCategoriaPlatoBase):
    id: int
    created_at: str
    categoria: CategoriaMenuResponse
    plato: PlatoRestauranteResponse
    
    class Config:
        from_attributes = True


# Esquemas especiales para la vista de meseros
class MenuDelDiaCompleto(BaseModel):
    """Menú del día completo para meseros"""
    menu: Optional[MenuDiaResponse] = None
    categorias: Dict[str, List[PlatoRestauranteResponse]] = Field(
        default_factory=dict,
        description="Platos organizados por categoría"
    )
    acompanamientos_fijos: List[AcompanamientoFijoResponse] = Field(
        default_factory=list,
        description="Acompañamientos que siempre se incluyen"
    )
    platos_fijos: List[PlatoRestauranteResponse] = Field(
        default_factory=list,
        description="Platos fijos independientes del menú"
    )
    mensaje: Optional[str] = None


class PedidoMenuDia(BaseModel):
    """Estructura para crear un pedido del menú del día"""
    menu_dia_id: int
    principio_id: int = Field(..., description="ID del plato de principio seleccionado")
    proteina_id: int = Field(..., description="ID del plato de proteína seleccionado")
    platos_fijos_ids: List[int] = Field(
        default_factory=list,
        description="IDs de platos fijos adicionales"
    )
    observaciones: Optional[str] = Field(None, max_length=500)


# Esquemas para respuestas de listas
class CategoriaMenuListResponse(BaseModel):
    categorias: List[CategoriaMenuResponse]
    total: int
    
    class Config:
        from_attributes = True


class PlatoRestauranteListResponse(BaseModel):
    platos: List[PlatoRestauranteResponse]
    total: int


class MenuDiaListResponse(BaseModel):
    menus: List[MenuDiaResponse]
    total: int


class AcompanamientoFijoListResponse(BaseModel):
    acompanamientos: List[AcompanamientoFijoResponse]
    total: int
