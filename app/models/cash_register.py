"""
Modelo para el sistema de caja - Simplificado y Profesional
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class CashStatus(str, enum.Enum):
    """Estados de caja"""
    OPEN = "abierta"
    CLOSED = "cerrada"


class MovementType(str, enum.Enum):
    """Tipos de movimiento de caja"""
    OPENING = "apertura"
    CLOSING = "cierre"
    SALE = "venta"
    REFUND = "devolución"
    EXPENSE = "gasto"
    WITHDRAWAL = "retiro"
    DEPOSIT = "depósito"


class CashRegister(Base):
    """Modelo para la caja registradora - Una sola caja por ubicación"""
    __tablename__ = "cash_registers"
    
    id = Column(Integer, primary_key=True, index=True)
    register_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, default="Caja Principal")
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    sessions = relationship("CashSession", back_populates="cash_register")
    
    def __repr__(self):
        return f"<CashRegister(id={self.id}, name='{self.name}')>"


class CashSession(Base):
    """Modelo para las sesiones de caja - Una sesión por día"""
    __tablename__ = "cash_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    cash_register_id = Column(Integer, ForeignKey("cash_registers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Apertura
    opening_amount = Column(Numeric(10, 2), nullable=False, default=0)
    opening_notes = Column(Text, nullable=True)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Cierre
    closing_amount = Column(Numeric(10, 2), nullable=True)
    closing_notes = Column(Text, nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Estado
    status = Column(String(20), default=CashStatus.OPEN)
    
    # Relaciones
    cash_register = relationship("CashRegister", back_populates="sessions")
    user = relationship("User", backref="cash_sessions")
    movements = relationship("CashMovement", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CashSession(id={self.id}, number='{self.session_number}', status='{self.status}')>"
    
    @property
    def total_sales(self):
        """Total de ventas en esta sesión"""
        return sum(
            movement.amount for movement in self.movements 
            if movement.movement_type == MovementType.SALE
        )
    
    @property
    def total_expenses(self):
        """Total de gastos en esta sesión"""
        return sum(
            movement.amount for movement in self.movements 
            if movement.movement_type == MovementType.EXPENSE
        )
    
    @property
    def expected_amount(self):
        """Monto esperado en caja"""
        return self.opening_amount + self.total_sales - self.total_expenses


class CashMovement(Base):
    """Modelo para los movimientos de caja"""
    __tablename__ = "cash_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("cash_sessions.id"), nullable=False)
    movement_type = Column(String(20), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=False)
    reference = Column(String(100), nullable=True)  # ID de venta, factura, etc.
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    session = relationship("CashSession", back_populates="movements")
    
    def __repr__(self):
        return f"<CashMovement(id={self.id}, type='{self.movement_type}', amount={self.amount})>"
