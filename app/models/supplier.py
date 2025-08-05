"""
Modelos de Proveedores, Compras e Items de Compra
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PurchaseStatus(str, enum.Enum):
    """Estados de compra"""
    PENDIENTE = "pendiente"
    RECIBIDA = "recibida"
    CANCELADA = "cancelada"
    PARCIAL = "parcial"


class Supplier(Base):
    """Modelo de Proveedor"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    document_type = Column(String(20), nullable=False)  # NIT, CC, etc.
    document_number = Column(String(20), unique=True, index=True, nullable=False)
    contact_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    credit_limit = Column(Numeric(10, 2), default=0)
    current_balance = Column(Numeric(10, 2), default=0)
    payment_terms = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    purchases = relationship("Purchase", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}', document='{self.document_number}')>"


class Purchase(Base):
    """Modelo de Compra"""
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_number = Column(String(50), unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    subtotal = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), default=0)
    
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.PENDIENTE)
    invoice_number = Column(String(50), nullable=True)
    invoice_date = Column(DateTime, nullable=True)
    expected_delivery = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    received_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    supplier = relationship("Supplier", back_populates="purchases")
    user = relationship("User")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Purchase(id={self.id}, purchase_number='{self.purchase_number}', total={self.total})>"


class PurchaseItem(Base):
    """Modelo de Item de Compra"""
    __tablename__ = "purchase_items"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    
    received_quantity = Column(Integer, default=0)
    lot_number = Column(String(50), nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<PurchaseItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>" 