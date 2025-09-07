"""
Modelos para Ventas
"""
import enum
from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class SaleStatus(str, enum.Enum):
    """Estados de venta"""
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    DEVUELTA = "devuelta"


class PaymentMethodType(str, enum.Enum):
    """Tipos de método de pago"""
    EFECTIVO = "efectivo"
    NEQUI = "nequi"
    DAVIPLATA = "daviplata"
    ADDI = "addi"
    SISTICREDITO = "sisticredito"
    RAPPI = "rappi"
    DIDI = "didi"
    FOOD = "food"
    TRANSFERENCIA = "transferencia"
    TARJETA_CREDITO = "tarjeta_credito"
    TARJETA_DEBITO = "tarjeta_debito"


class Sale(Base):
    """Modelo de Venta - Simplificado"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Campos de cálculo
    subtotal = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), default=0)
    tip = Column(Numeric(10, 2), default=0)
    commission = Column(Numeric(10, 2), default=0)
    
    # Estado
    status = Column(String(10), default=SaleStatus.PENDIENTE)
    
    # Relaciones
    customer = relationship("Customer", back_populates="sales")
    user = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("PaymentMethod", back_populates="sale", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sale(id={self.id}, sale_number='{self.sale_number}', total={self.total})>"


class SaleItem(Base):
    """Modelo de Item de Venta"""
    __tablename__ = "sale_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<SaleItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"


class PaymentMethod(Base):
    """Modelo de Método de Pago"""
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    payment_type = Column(String(20), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    sale = relationship("Sale", back_populates="payments")
    
    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, type='{self.payment_type}', amount={self.amount})>" 