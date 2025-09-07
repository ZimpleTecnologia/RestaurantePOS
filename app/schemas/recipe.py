"""
Esquemas Pydantic para Recetas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class RecipeItemBase(BaseModel):
    """Esquema base para items de receta"""
    product_id: int = Field(..., gt=0, description="ID del producto ingrediente")
    quantity: float = Field(..., gt=0, description="Cantidad del ingrediente")
    unit: str = Field("unidad", max_length=20, description="Unidad de medida")
    is_optional: bool = Field(False, description="Si el ingrediente es opcional")
    notes: Optional[str] = Field(None, max_length=500, description="Notas del ingrediente")


class RecipeItemCreate(RecipeItemBase):
    """Esquema para crear item de receta"""
    pass


class RecipeItemUpdate(BaseModel):
    """Esquema para actualizar item de receta"""
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    is_optional: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class RecipeItemResponse(RecipeItemBase):
    """Esquema de respuesta para item de receta"""
    id: int
    recipe_id: int
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None
    created_at: datetime
    
    # Información del producto
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    product_type: Optional[str] = None
    
    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    """Esquema base para recetas"""
    name: str = Field(..., min_length=1, max_length=200, description="Nombre de la receta")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción de la receta")
    preparation_time: int = Field(0, ge=0, description="Tiempo de preparación en minutos")
    instructions: Optional[str] = Field(None, max_length=2000, description="Instrucciones de preparación")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")


class RecipeCreate(RecipeBase):
    """Esquema para crear receta"""
    product_id: int = Field(..., gt=0, description="ID del producto al que pertenece la receta")
    items: List[RecipeItemCreate] = Field(..., min_items=1, description="Lista de ingredientes")


class RecipeUpdate(BaseModel):
    """Esquema para actualizar receta"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    preparation_time: Optional[int] = Field(None, ge=0)
    instructions: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


class RecipeResponse(RecipeBase):
    """Esquema de respuesta para receta"""
    id: int
    product_id: int
    is_active: bool
    total_cost: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Información del producto
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    
    # Items de la receta
    items: List[RecipeItemResponse] = []
    
    class Config:
        from_attributes = True


class RecipeWithItems(RecipeResponse):
    """Esquema de receta con items detallados"""
    items: List[RecipeItemResponse] = []


class RecipeCostCalculation(BaseModel):
    """Esquema para cálculo de costo de receta"""
    recipe_id: int
    total_cost: float
    ingredients: List[RecipeItemResponse]
    last_updated: datetime


class InventoryConsumptionRequest(BaseModel):
    """Esquema para solicitud de consumo de inventario"""
    product_id: int = Field(..., gt=0, description="ID del producto a vender")
    quantity: int = Field(..., gt=0, description="Cantidad a vender")
    sale_id: Optional[int] = Field(None, description="ID de la venta")


class InventoryConsumptionResponse(BaseModel):
    """Esquema para respuesta de consumo de inventario"""
    success: bool
    message: str
    consumed_items: List[dict]
    total_cost: Optional[float] = None
    insufficient_stock: Optional[List[dict]] = None


class InventoryAvailabilityCheck(BaseModel):
    """Esquema para verificación de disponibilidad de inventario"""
    product_id: int = Field(..., gt=0, description="ID del producto")
    quantity: int = Field(..., gt=0, description="Cantidad a verificar")


class InventoryAvailabilityResponse(BaseModel):
    """Esquema para respuesta de disponibilidad de inventario"""
    available: bool
    message: str
    ingredients: List[dict]
