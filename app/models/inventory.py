"""
Modelos de Inventario y Movimientos de Inventario
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class MovementType(str, enum.Enum):
    """Tipos de movimiento de inventario"""
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"
    TRANSFERENCIA = "transferencia"
    DEVOLUCION = "devolucion"


class InventoryMovement(Base):
    """Modelo de Movimiento de Inventario"""
    __tablename__ = "inventory_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    adjustment_type = Column(String(20), nullable=False)  # 'add', 'subtract', 'set'
    quantity = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    product = relationship("Product", back_populates="inventory_movements")
    user = relationship("User")
    
    def __repr__(self):
        return f"<InventoryMovement(id={self.id}, type='{self.adjustment_type}', quantity={self.quantity})>" 