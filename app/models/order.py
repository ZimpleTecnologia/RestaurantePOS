"""
Modelo para los pedidos del restaurante
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
from decimal import Decimal


class OrderStatus(str, enum.Enum):
    """Estados de los pedidos"""
    PENDING = "pendiente"         # Pedido tomado, esperando cocina
    PREPARING = "preparando"      # En cocina
    READY = "listo"              # Listo para servir
    SERVED = "servido"           # Ya servido al cliente
    PAID = "pagado"              # Pedido pagado
    CANCELLED = "cancelado"      # Pedido cancelado


class OrderType(str, enum.Enum):
    """Tipos de pedido"""
    DINE_IN = "mesa"             # Pedido en mesa
    TAKEAWAY = "para_llevar"     # Para llevar
    DELIVERY = "domicilio"       # Domicilio


class Order(Base):
    """Modelo para los pedidos del restaurante"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), unique=True, nullable=False, index=True)
    
    # Relaciones
    table_id = Column(Integer, ForeignKey("restaurant_tables.id"), nullable=True)  # Null para takeaway/delivery
    waiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    
    # Información del pedido
    order_type = Column(Enum(OrderType), default=OrderType.DINE_IN)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Numeric(10, 2), default=Decimal('0.00'))
    tax_amount = Column(Numeric(10, 2), default=Decimal('0.00'))
    discount_amount = Column(Numeric(10, 2), default=Decimal('0.00'))
    final_amount = Column(Numeric(10, 2), default=Decimal('0.00'))
    
    # Información adicional
    customer_name = Column(String(100), nullable=True)  # Para pedidos sin cliente registrado
    customer_phone = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)  # Notas especiales del pedido
    
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


class OrderItem(Base):
    """Modelo para los items de un pedido"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Información del item
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Personalizaciones
    notes = Column(Text, nullable=True)  # Notas específicas del item
    special_instructions = Column(Text, nullable=True)  # Instrucciones especiales
    
    # Estado del item
    is_ready = Column(Boolean, default=False)  # Si está listo en cocina
    is_served = Column(Boolean, default=False)  # Si ya fue servido
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product", backref="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, product='{self.product.name}', quantity={self.quantity})>"
    
    def calculate_total(self):
        """Calcular precio total del item"""
        self.total_price = self.unit_price * self.quantity
        return self.total_price
