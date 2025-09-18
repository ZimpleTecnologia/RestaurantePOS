"""
Modelo de Producto para el sistema POS
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from decimal import Decimal


class ProductCategory(str, enum.Enum):
    """Categorías de productos"""
    ENTRADA = "entrada"
    PLATO_PRINCIPAL = "plato_principal"
    POSTRE = "postre"
    BEBIDA = "bebida"
    ALCOHOL = "alcohol"
    INGREDIENTE = "ingrediente"
    UTENSILIO = "utensilio"
    OTRO = "otro"


class ProductType(str, enum.Enum):
    """Tipos de productos"""
    INVENTORY = "inventory"  # Materias primas (Arroz, Pollo, Carne, etc.)
    SALES = "sales"         # Productos de venta (Platos preparados)


class Category(Base):
    """Modelo de Categoría de Productos"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    subcategories = relationship("SubCategory", back_populates="category")
    products = relationship("Product", back_populates="category_rel")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class SubCategory(Base):
    """Modelo de Subcategoría de Productos"""
    __tablename__ = "subcategories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory_rel")
    
    def __repr__(self):
        return f"<SubCategory(id={self.id}, name='{self.name}', category_id={self.category_id})>"


class Product(Base):
    """Modelo de Producto - Reestructurado según especificaciones"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    precio_base = Column(Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    cost_price = Column(Numeric(10, 2), nullable=True)  # Precio de costo para cálculo de ganancias
    
    # Nuevos campos según especificaciones
    es_fijo = Column(Boolean, default=True)  # TRUE si es parte de la carta permanente
    activo = Column(Boolean, default=True)   # para habilitar/deshabilitar un plato sin borrarlo
    
    # Tipo de producto (materia prima o producto de venta)
    product_type = Column(Enum(ProductType), default=ProductType.SALES, nullable=False)
    
    # Código del producto
    code = Column(String(50), unique=True, nullable=True, index=True)  # Código interno del producto
    
    # Códigos de barras y SKU
    barcode = Column(String(50), unique=True, nullable=True, index=True)  # Código de barras
    sku = Column(String(50), unique=True, nullable=True, index=True)  # Stock Keeping Unit
    
    # Categorización (compatibilidad con enum y tablas)
    category = Column(Enum(ProductCategory), default=ProductCategory.OTRO)
    subcategory = Column(String(50), nullable=True)
    
    # Relaciones con tablas de categorías (para compatibilidad)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True)
    
    # Control de inventario
    track_stock = Column(Boolean, default=True)  # Si se debe rastrear stock (por defecto True)
    stock_quantity = Column(Integer, default=0)  # Cantidad actual en stock
    min_stock_level = Column(Integer, default=0)  # Nivel mínimo de stock para alertas
    max_stock_level = Column(Integer, default=0)  # Nivel máximo de stock
    reorder_point = Column(Integer, default=0)  # Punto de reorden
    
    # Campos específicos para materias primas
    purchase_price = Column(Numeric(10, 2), nullable=True)  # Precio de compra para materias primas
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    supplier = Column(String(100), nullable=True)  # Nombre del proveedor como string
    
    # Campos de stock para compatibilidad con el router
    stock = Column(Integer, default=0)  # Alias para stock_quantity
    min_stock = Column(Integer, default=0)  # Alias para min_stock_level
    max_stock = Column(Integer, default=100)  # Alias para max_stock_level
    
    # Unidades y medidas
    unit = Column(String(20), default="unidad")  # unidad, kg, litro, etc.
    weight = Column(Numeric(8, 3), nullable=True)  # Peso en kg
    volume = Column(Numeric(8, 3), nullable=True)  # Volumen en litros
    
    # Imagen y estado
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # Para destacar en menú
    
    # Información nutricional (opcional)
    calories = Column(Integer, nullable=True)
    protein = Column(Numeric(5, 2), nullable=True)
    carbs = Column(Numeric(5, 2), nullable=True)
    fat = Column(Numeric(5, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    supplier_rel = relationship("Supplier", backref="products")
    category_rel = relationship("Category", back_populates="products")
    subcategory_rel = relationship("SubCategory", back_populates="products")
    inventory_lots = relationship("InventoryLot", back_populates="product")
    order_items = relationship("OrderItem", overlaps="order_items,product")
    sale_items = relationship("SaleItem", overlaps="sale_items,product")
    recipe_items = relationship("RecipeItem", back_populates="product")
    recipe = relationship("Recipe", back_populates="product", uselist=False)
    
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', precio_base={self.precio_base})>"
    
    @property
    def is_low_stock(self):
        """Verificar si el producto tiene stock bajo"""
        if not self.track_stock:
            return False
        return self.stock_quantity <= self.min_stock_level
    
    @property
    def is_out_of_stock(self):
        """Verificar si el producto está agotado"""
        if not self.track_stock:
            return False
        return self.stock_quantity <= 0
    
    @property
    def stock_status(self):
        """Obtener estado del stock como string"""
        if not self.track_stock:
            return "no_tracked"
        if self.stock_quantity <= 0:
            return "out_of_stock"
        if self.stock_quantity <= self.min_stock_level:
            return "low_stock"
        return "in_stock"
    
    @property
    def needs_reorder(self):
        """Verificar si necesita reorden"""
        if not self.track_stock:
            return False
        return self.stock_quantity <= self.reorder_point
    
    def update_stock(self, quantity_change):
        """Actualizar stock del producto"""
        if self.track_stock:
            self.stock_quantity = max(0, self.stock_quantity + quantity_change)
            return True
        return False
    
    def calculate_margin(self):
        """Calcular margen de ganancia"""
        if self.cost_price and self.precio_base > 0:
            return ((self.precio_base - self.cost_price) / self.precio_base) * 100
        return 0
    
    def get_stock_alert_message(self):
        """Obtener mensaje de alerta de stock"""
        if not self.track_stock:
            return None
        
        if self.stock_quantity <= 0:
            return f"⚠️ {self.name} está AGOTADO"
        elif self.stock_quantity <= self.min_stock_level:
            return f"⚠️ {self.name} tiene stock bajo ({self.stock_quantity} {self.unit})"
        elif self.needs_reorder:
            return f"📦 {self.name} necesita reorden ({self.stock_quantity} {self.unit})"
        
        return None
    
    @property
    def is_inventory_product(self):
        """Verificar si es un producto de inventario (materia prima)"""
        return self.product_type == ProductType.INVENTORY
    
    @property
    def is_sales_product(self):
        """Verificar si es un producto de venta (plato preparado)"""
        return self.product_type == ProductType.SALES
    
    def can_consume_inventory(self):
        """Verificar si este producto puede consumir inventario (tiene receta)"""
        return self.is_sales_product and len(self.recipe_items) > 0 