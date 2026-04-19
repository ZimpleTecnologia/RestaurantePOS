"""
Modelo para los pedidos del restaurante

Sistema unificado de pedidos que reemplaza al antiguo PedidoCocina.
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
from decimal import Decimal
from datetime import datetime


class OrderStatus(str, enum.Enum):
    """Estados de los pedidos - unificados"""
    DRAFT = "borrador"           # Pedido en creación por el mesero
    PENDING = "pendiente"        # Pedido tomado, esperando cocina
    CONFIRMED = "confirmado"     # Confirmado para envío a cocina
    PREPARING = "preparando"     # En cocina
    READY = "listo"             # Listo para servir
    SERVED = "servido"           # Ya servido al cliente
    PAID = "pagado"              # Pedido pagado
    CANCELLED = "cancelado"      # Pedido cancelado


class OrderType(str, enum.Enum):
    """Tipos de pedido"""
    DINE_IN = "mesa"             # Pedido en mesa
    TAKEAWAY = "para_llevar"     # Para llevar
    DELIVERY = "domicilio"       # Domicilio


class OrderSource(str, enum.Enum):
    """Origen del pedido"""
    POS = "pos"                  # Sistema POS
    KITCHEN = "cocina"           #直接在 cocina
    KIOSK = "kiosco"             # Kiosco de autoatención
    APP = "app"                  # App móvil


class Order(Base):
    """Modelo unificado para los pedidos del restaurante"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(20), unique=True, nullable=False)
    
    # Relaciones - mesa principal (Table de location.py)
    # NOTA: mesa_id está deprecated, usar table_id
    table_id = Column(Integer, ForeignKey("restaurant_tables.id"), nullable=True)
    waiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    
    # Información del pedido
    order_type = Column(Enum(OrderType), default=OrderType.DINE_IN)
    source = Column(Enum(OrderSource), default=OrderSource.POS)
    status = Column(Enum(OrderStatus), default=OrderStatus.DRAFT)
    
    # Campos de cocina (antes en PedidoCocina)
    hora_envio = Column(DateTime(timezone=True), nullable=True)
    hora_inicio_preparacion = Column(DateTime(timezone=True), nullable=True)
    hora_finalizacion = Column(DateTime(timezone=True), nullable=True)
    
    # Información financiera
    total_amount = Column(Numeric(10, 2), default=Decimal('0.00'))
    tax_amount = Column(Numeric(10, 2), default=Decimal('0.00'))
    discount_amount = Column(Numeric(10, 2), default=Decimal('0.00'))
    final_amount = Column(Numeric(10, 2), default=Decimal('0.00'))
    
    # Información adicional
    customer_name = Column(String(100), nullable=True)
    customer_phone = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    served_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    table = relationship("Table", back_populates="orders")
    waiter = relationship("User", backref="orders_served")
    customer = relationship("Customer", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, number='{self.order_number}', status='{self.status}')>"
    
    @property
    def is_active(self):
        """Verificar si el pedido está activo (no pagado ni cancelado)"""
        return self.status not in [OrderStatus.PAID, OrderStatus.CANCELLED]
    
    @property
    def is_pending_payment(self):
        """Verificar si el pedido está pendiente de pago"""
        return self.status == OrderStatus.SERVED
    
    @property
    def can_be_served(self):
        """Verificar si el pedido puede ser servido"""
        return self.status == OrderStatus.READY
    
    @property
    def can_be_paid(self):
        """Verificar si el pedido puede ser pagado"""
        return self.status == OrderStatus.SERVED
    
    def calculate_totals(self):
        """Calcular totales del pedido"""
        subtotal = sum(item.total_price for item in self.items)
        self.total_amount = subtotal
        self.tax_amount = subtotal * Decimal('0.19')  # 19% IVA
        self.final_amount = self.total_amount + self.tax_amount - self.discount_amount
        return self.final_amount


class ItemType(str, enum.Enum):
    """Tipos de item en el pedido"""
    PRODUCT = "product"           # Producto directo del inventario
    MENU = "menu"               # Menú del día
    PLATO = "plato"             # Plato especial de la carta


class OrderItem(Base):
    """Modelo unificado para los items de un pedido"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Tipo de item (PRODUCT, MENU, PLATO)
    item_type = Column(Enum(ItemType), default=ItemType.PRODUCT)
    
    # Referencias - dependiendo del tipo de item
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    menu_id = Column(Integer, ForeignKey("menus_dia.id"), nullable=True)
    plato_id = Column(Integer, ForeignKey("platos_restaurante.id"), nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias_menu.id"), nullable=True)
    
    # Snapshots para preservar información histórica
    snapshot_name = Column(String(200), nullable=True)
    snapshot_description = Column(Text, nullable=True)
    snapshot_price = Column(Numeric(10, 2), nullable=True)
    
    # Información del item
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Personalizaciones
    notes = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    
    # Estado del item
    is_ready = Column(Boolean, default=False)
    is_served = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    menu = relationship("MenuDia")
    plato = relationship("PlatoRestaurante")
    categoria = relationship("CategoriaMenuRestaurante")
    opciones = relationship("OrderItemOption", back_populates="order_item", cascade="all, delete-orphan")
    
    def __repr__(self):
        name = self.snapshot_name or (self.product.name if self.product else "Unknown")
        return f"<OrderItem(id={self.id}, name='{name}', quantity={self.quantity})>"
    
    def calculate_total(self):
        """Calcular precio total del item"""
        self.total_price = self.unit_price * self.quantity
        return self.total_price
    
    def create_snapshot(self):
        """Crear snapshot del item al momento de agregar al pedido"""
        if self.product:
            self.snapshot_name = self.product.name
            self.snapshot_description = self.product.description
            self.snapshot_price = self.product.price
        elif self.plato:
            self.snapshot_name = self.plato.nombre
            self.snapshot_description = self.plato.descripcion
            self.snapshot_price = self.plato.precio


class OrderItemOption(Base):
    """Opciones seleccionadas para un item de menú"""
    __tablename__ = "order_item_opciones"
    
    id = Column(Integer, primary_key=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False)
    
    # Categoría y opción elegida (snapshots)
    categoria = Column(String(50), nullable=False)
    opcion_elegida = Column(String(200), nullable=False)
    opcion_plato_id = Column(Integer, ForeignKey("platos_restaurante.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    order_item = relationship("OrderItem", back_populates="opciones")
    plato = relationship("PlatoRestaurante")
    
    def __repr__(self):
        return f"<OrderItemOption(categoria='{self.categoria}', opcion='{self.opcion_elegida}')>"
