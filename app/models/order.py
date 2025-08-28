"""
Modelos para Órdenes de Restaurante - Simplificados
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    """Estados de orden"""
    PENDIENTE = "pendiente"
    EN_PREPARACION = "en_preparacion"
    LISTO = "listo"
    SERVIDO = "servido"
    CANCELADO = "cancelado"


class OrderPriority(str, enum.Enum):
    """Prioridades de orden"""
    BAJA = "baja"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


class Order(Base):
    """Modelo de Orden de Restaurante - Simplificado"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    waiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la orden
    people_count = Column(Integer, default=1)
    status = Column(String(20), default="pendiente")
    priority = Column(String(20), default="normal")
    
    # Notas y observaciones
    notes = Column(Text, nullable=True)
    kitchen_notes = Column(Text, nullable=True)
    
    # Tiempos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    kitchen_start_time = Column(DateTime(timezone=True), nullable=True)
    kitchen_end_time = Column(DateTime(timezone=True), nullable=True)
    served_time = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    table = relationship("Table", back_populates="orders")
    waiter = relationship("User", foreign_keys=[waiter_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, number='{self.order_number}', status='{self.status}')>"


class OrderItem(Base):
    """Modelo de Item de Orden"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=True)  # Columna adicional si existe en la BD
    
    # Estado específico del item
    status = Column(String(20), default="pendiente")
    special_instructions = Column(Text, nullable=True)
    
    # Tiempos específicos del item
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    kitchen_start_time = Column(DateTime(timezone=True), nullable=True)
    kitchen_end_time = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
