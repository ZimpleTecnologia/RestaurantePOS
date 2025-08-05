"""
Modelos de Clientes, Créditos y Pagos
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Customer(Base):
    """Modelo de Cliente"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(20), nullable=False)  # CC, CE, NIT, etc.
    document_number = Column(String(20), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    credit_limit = Column(Numeric(10, 2), default=0)
    current_balance = Column(Numeric(10, 2), default=0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    sales = relationship("Sale", back_populates="customer")
    credits = relationship("Credit", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.full_name}', document='{self.document_number}')>"


class Credit(Base):
    """Modelo de Crédito"""
    __tablename__ = "credits"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    
    amount = Column(Numeric(10, 2), nullable=False)
    balance = Column(Numeric(10, 2), nullable=False)
    due_date = Column(Date, nullable=True)
    interest_rate = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    customer = relationship("Customer", back_populates="credits")
    sale = relationship("Sale")
    payments = relationship("Payment", back_populates="credit")
    
    def __repr__(self):
        return f"<Credit(id={self.id}, customer_id={self.customer_id}, amount={self.amount}, balance={self.balance})>"


class Payment(Base):
    """Modelo de Pago"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    credit_id = Column(Integer, ForeignKey("credits.id"), nullable=True)
    
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    customer = relationship("Customer", back_populates="payments")
    credit = relationship("Credit", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, customer_id={self.customer_id}, amount={self.amount})>" 