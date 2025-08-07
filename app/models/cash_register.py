"""
Modelo para el sistema de caja
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# Constantes para los valores de estado y tipo de movimiento
CASH_REGISTER_STATUS = {
    'OPEN': 'abierta',
    'CLOSED': 'cerrada'
}

CASH_MOVEMENT_TYPE = {
    'OPENING': 'apertura',
    'CLOSING': 'cierre',
    'SALE': 'venta',
    'REFUND': 'devolución',
    'EXPENSE': 'gasto',
    'WITHDRAWAL': 'retiro',
    'DEPOSIT': 'depósito'
}


class CashRegister(Base):
    """Modelo para la caja registradora"""
    __tablename__ = "cash_registers"
    
    id = Column(Integer, primary_key=True, index=True)
    register_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CashSession(Base):
    """Modelo para las sesiones de caja"""
    __tablename__ = "cash_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    cash_register_id = Column(Integer, ForeignKey("cash_registers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Apertura
    opening_amount = Column(Numeric(10, 2), nullable=False)
    opening_notes = Column(Text, nullable=True)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Cierre
    closing_amount = Column(Numeric(10, 2), nullable=True)
    closing_notes = Column(Text, nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Estado
    status = Column(String(20), default=CASH_REGISTER_STATUS['OPEN'])
    
    # Relaciones
    cash_register = relationship("CashRegister", backref="sessions")
    user = relationship("User", backref="cash_sessions")
    movements = relationship("CashMovement", back_populates="session")


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
