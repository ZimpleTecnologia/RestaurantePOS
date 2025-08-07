"""
Esquemas Pydantic para Productos y Categorías
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.product import ProductType


class CategoryBase(BaseModel):
    """Esquema base para categorías"""
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Esquema para crear categoría"""
    pass


class CategoryUpdate(BaseModel):
    """Esquema para actualizar categoría"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Esquema de respuesta para categoría"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubCategoryBase(BaseModel):
    """Esquema base para subcategorías"""
    name: str
    description: Optional[str] = None
    category_id: int


class SubCategoryCreate(SubCategoryBase):
    """Esquema para crear subcategoría"""
    pass


class SubCategoryUpdate(BaseModel):
    """Esquema para actualizar subcategoría"""
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class SubCategoryResponse(SubCategoryBase):
    """Esquema de respuesta para subcategoría"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Esquema base para productos"""
    code: str
    name: str
    description: Optional[str] = None
    price: float
    cost_price: Optional[float] = None
    stock: int = 0
    min_stock: int = 0
    max_stock: int = 1000
    category_id: int
    subcategory_id: Optional[int] = None
    product_type: ProductType = ProductType.PRODUCTO
    image_url: Optional[str] = None
    has_recipe: bool = False


class ProductCreate(ProductBase):
    """Esquema para crear producto"""
    pass


class ProductUpdate(BaseModel):
    """Esquema para actualizar producto"""
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    product_type: Optional[ProductType] = None
    image_url: Optional[str] = None
    has_recipe: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Esquema de respuesta para producto"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductWithCategory(ProductResponse):
    """Esquema de producto con información de categoría"""
    category: Optional[CategoryResponse] = None
    subcategory: Optional[SubCategoryResponse] = None 