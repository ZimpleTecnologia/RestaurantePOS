"""
Esquemas Pydantic para Productos y Categorías
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.product import ProductCategory, ProductType


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
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    stock: int = 0
    min_stock: int = 0
    max_stock: int = 1000
    stock_quantity: Optional[int] = None  # Para compatibilidad con frontend
    min_stock_level: Optional[int] = None  # Para compatibilidad con frontend
    unit: Optional[str] = None  # Unidad de medida
    category_id: int
    subcategory_id: Optional[int] = None
    category: ProductCategory = ProductCategory.OTRO
    product_type: ProductType = ProductType.SALES
    purchase_price: Optional[float] = None  # Para materias primas
    supplier_id: Optional[int] = None
    supplier: Optional[str] = None  # Nombre del proveedor como string
    image_url: Optional[str] = None
    has_recipe: bool = False
    is_active: bool = True


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
    stock_quantity: Optional[int] = None  # Para compatibilidad con frontend
    min_stock_level: Optional[int] = None  # Para compatibilidad con frontend
    unit: Optional[str] = None  # Unidad de medida
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    category: Optional[ProductCategory] = None
    product_type: Optional[ProductType] = None
    purchase_price: Optional[float] = None
    supplier_id: Optional[int] = None
    supplier: Optional[str] = None  # Nombre del proveedor como string
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


class InventoryProductResponse(BaseModel):
    """Esquema específico para productos de inventario"""
    id: int
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    product_type: str = "inventory"  # Valor por defecto
    category_id: Optional[int] = None
    stock_quantity: int = 0
    min_stock_level: int = 0
    max_stock_level: int = 100
    stock: int = 0
    min_stock: int = 0
    max_stock: int = 100
    unit: str = "unidad"
    purchase_price: Optional[float] = None
    supplier_id: Optional[int] = None
    supplier: Optional[str] = None  # Nombre del proveedor como string
    barcode: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductWithCategory(ProductResponse):
    """Esquema de producto con información de categoría"""
    category: Optional[CategoryResponse] = None
    subcategory: Optional[SubCategoryResponse] = None 