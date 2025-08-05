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


class Inventory(Base):
    """Modelo de Inventario"""
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    current_stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    max_stock = Column(Integer, default=1000)
    lot_number = Column(String(50), nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    product = relationship("Product")
    location = relationship("Location")
    movements = relationship("InventoryMovement", back_populates="inventory")
    
    def __repr__(self):
        return f"<Inventory(id={self.id}, product_id={self.product_id}, stock={self.current_stock})>"


class InventoryMovement(Base):
    """Modelo de Movimiento de Inventario"""
    __tablename__ = "inventory_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(10, 2), nullable=True)
    
    reference_type = Column(String(50), nullable=True)  # sale, purchase, adjustment, etc.
    reference_id = Column(Integer, nullable=True)
    lot_number = Column(String(50), nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    inventory = relationship("Inventory", back_populates="movements")
    product = relationship("Product", back_populates="inventory_movements")
    user = relationship("User", back_populates="inventory_movements")
    
    def __repr__(self):
        return f"<InventoryMovement(id={self.id}, type='{self.movement_type}', quantity={self.quantity})>" 