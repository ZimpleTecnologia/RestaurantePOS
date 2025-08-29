"""
Modelos de Productos, Categorías y Subcategorías
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ProductType(str, enum.Enum):
    """Tipos de producto"""
    PRODUCTO = "producto"
    SERVICIO = "servicio"
    COMBO = "combo"


class Category(Base):
    """Modelo de Categoría"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    subcategories = relationship("SubCategory", back_populates="category")
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class SubCategory(Base):
    """Modelo de Subcategoría"""
    __tablename__ = "subcategories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory")
    
    def __repr__(self):
        return f"<SubCategory(id={self.id}, name='{self.name}', category_id={self.category_id})>"


class Product(Base):
    """Modelo de Producto - Versión Mejorada"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=True)
    stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    max_stock = Column(Integer, default=1000)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True)
    product_type = Column(Enum(ProductType), default=ProductType.PRODUCTO)
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    has_recipe = Column(Boolean, default=False)
    
    # Configuración de inventario
    track_lots = Column(Boolean, default=False)  # Si requiere trazabilidad por lotes
    track_expiration = Column(Boolean, default=False)  # Si requiere control de caducidad
    shelf_life_days = Column(Integer, nullable=True)  # Vida útil en días
    reorder_point = Column(Integer, default=0)  # Punto de reorden
    reorder_quantity = Column(Integer, default=0)  # Cantidad de reorden
    
    # Configuración de ubicación
    default_location_id = Column(Integer, ForeignKey("inventory_locations.id"), nullable=True)
    
    # Metadatos
    barcode = Column(String(100), nullable=True)
    sku = Column(String(100), nullable=True)
    weight = Column(Float, nullable=True)  # Peso en kg
    dimensions = Column(String(50), nullable=True)  # Dimensiones (LxWxH)
    unit_of_measure = Column(String(20), default="unidad")  # unidad, kg, litros, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    category = relationship("Category", back_populates="products")
    subcategory = relationship("SubCategory", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    inventory_movements = relationship("InventoryMovement", back_populates="product")
    inventory_lots = relationship("InventoryLot", back_populates="product")
    recipe_items = relationship("RecipeItem", back_populates="product")
    default_location = relationship("InventoryLocation")
    
    def __repr__(self):
        return f"<Product(id={self.id}, code='{self.code}', name='{self.name}')>"
    
    @property
    def total_stock_value(self) -> float:
        """Valor total del stock actual"""
        return self.stock * (self.cost_price or 0)
    
    @property
    def stock_status(self) -> str:
        """Estado del stock"""
        if self.stock == 0:
            return "out_of_stock"
        elif self.stock <= self.min_stock:
            return "low_stock"
        elif self.stock >= self.max_stock:
            return "overstock"
        else:
            return "normal"
    
    @property
    def needs_reorder(self) -> bool:
        """Verificar si necesita reorden"""
        return self.stock <= self.reorder_point 