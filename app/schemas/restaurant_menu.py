"""
Esquemas Pydantic para el sistema de menús del restaurante
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal


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


class PlatoRestauranteCreate(PlatoRestauranteBase):
    pass


class PlatoRestauranteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = Field(None, ge=0)
    tipo: Optional[str] = Field(None, pattern=r'^(Menu_Dia|Plato_Fijo|Acompanamiento_Fijo)$')
    activo: Optional[bool] = None


class PlatoRestauranteResponse(PlatoRestauranteBase):
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
            precio=obj.precio,
            tipo=obj.tipo,
            activo=obj.activo if obj.activo is not None else True,
            created_at=str(obj.created_at) if obj.created_at else None,
            updated_at=str(obj.updated_at) if obj.updated_at else None
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
class MenuDiaBase(BaseModel):
    fecha: date
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activo: bool = True
    publicado: bool = False


class MenuDiaCreate(MenuDiaBase):
    categorias_platos: List[Dict[str, List[int]]] = Field(
        ..., 
        description="Dict con categorías y sus platos: {'Principio': [1,2], 'Proteína': [3,4]}"
    )


class MenuDiaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    publicado: Optional[bool] = None
    categorias_platos: Optional[Dict[str, List[int]]] = None


class MenuDiaResponse(MenuDiaBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """Método personalizado para convertir desde ORM"""
        return cls(
            id=obj.id,  # Usar id del modelo
            fecha=str(obj.fecha),
            nombre=obj.nombre,
            precio=obj.precio,
            descripcion=obj.descripcion,
            activo=obj.estado == 'ACTIVE' if obj.estado else True,  # Mapear ACTIVE a activo
            publicado=obj.estado == 'ACTIVE' if obj.estado else False,  # Mapear ACTIVE a publicado
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
    menu: MenuDiaResponse
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
