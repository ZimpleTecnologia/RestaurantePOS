"""
Modelos de Inventario y Movimientos de Inventario - Versión Profesional
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric, Enum, Date, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import date, datetime
from typing import Optional


class MovementType(str, enum.Enum):
    """Tipos de movimiento de inventario"""
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"
    TRANSFERENCIA = "transferencia"
    DEVOLUCION = "devolucion"
    MERMA = "merma"
    CADUCIDAD = "caducidad"
    INVENTARIO_FISICO = "inventario_fisico"


class MovementReason(str, enum.Enum):
    """Razones específicas para movimientos de inventario"""
    # Entradas
    COMPRA_PROVEEDOR = "compra_proveedor"
    DEVOLUCION_CLIENTE = "devolucion_cliente"
    TRANSFERENCIA_ENTRADA = "transferencia_entrada"
    AJUSTE_POSITIVO = "ajuste_positivo"
    
    # Salidas
    VENTA = "venta"
    MERMA_NATURAL = "merma_natural"
    CADUCIDAD = "caducidad"
    TRANSFERENCIA_SALIDA = "transferencia_salida"
    AJUSTE_NEGATIVO = "ajuste_negativo"
    ROBOTES = "robotes"
    MUESTRAS = "muestras"


class InventoryLocation(Base):
    """Modelo de ubicaciones de inventario"""
    __tablename__ = "inventory_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    inventory_lots = relationship("InventoryLot", back_populates="location")
    
    def __repr__(self):
        return f"<InventoryLocation(id={self.id}, name='{self.name}')>"


class InventoryLot(Base):
    """Modelo de lotes de inventario para trazabilidad"""
    __tablename__ = "inventory_lots"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("inventory_locations.id"), nullable=False)
    
    lot_number = Column(String(50), nullable=False)
    batch_number = Column(String(50), nullable=True)
    supplier_lot = Column(String(50), nullable=True)
    
    quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    available_quantity = Column(Integer, nullable=False, default=0)
    
    unit_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(10, 2), nullable=True)
    
    manufacturing_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True)
    best_before_date = Column(Date, nullable=True)
    
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    purchase_order = Column(String(50), nullable=True)
    invoice_number = Column(String(50), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    product = relationship("Product", back_populates="inventory_lots")
    location = relationship("InventoryLocation", back_populates="inventory_lots")
    supplier = relationship("Supplier")
    movements = relationship("InventoryMovement", back_populates="lot")
    
    # Índices para optimización
    __table_args__ = (
        Index('idx_lot_product_location', 'product_id', 'location_id'),
        Index('idx_lot_expiration', 'expiration_date'),
        Index('idx_lot_number', 'lot_number'),
    )
    
    def __repr__(self):
        return f"<InventoryLot(id={self.id}, lot='{self.lot_number}', product_id={self.product_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Verificar si el lote está expirado"""
        if self.expiration_date:
            return self.expiration_date < date.today()
        return False
    
    @property
    def is_expiring_soon(self) -> bool:
        """Verificar si el lote expira pronto (30 días)"""
        if self.expiration_date:
            days_until_expiry = (self.expiration_date - date.today()).days
            return 0 <= days_until_expiry <= 30
        return False
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Días hasta la expiración"""
        if self.expiration_date:
            return (self.expiration_date - date.today()).days
        return None


class InventoryMovement(Base):
    """Modelo de Movimiento de Inventario - Versión Mejorada"""
    __tablename__ = "inventory_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Referencias
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("inventory_lots.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("inventory_locations.id"), nullable=True)
    
    # Datos del movimiento
    movement_type = Column(Enum(MovementType), nullable=False)
    reason = Column(Enum(MovementReason), nullable=False)
    reason_detail = Column(String(200), nullable=True)
    
    # Cantidades
    quantity = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    
    # Costos
    unit_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(10, 2), nullable=True)
    
    # Referencias externas
    reference_type = Column(String(50), nullable=True)  # 'sale', 'purchase', 'transfer', etc.
    reference_id = Column(Integer, nullable=True)
    reference_number = Column(String(50), nullable=True)
    
    # Metadatos
    notes = Column(Text, nullable=True)
    tags = Column(String(200), nullable=True)  # Para categorización adicional
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    product = relationship("Product", back_populates="inventory_movements")
    lot = relationship("InventoryLot", back_populates="movements")
    user = relationship("User", back_populates="inventory_movements")
    location = relationship("InventoryLocation")
    
    # Índices para optimización
    __table_args__ = (
        Index('idx_movement_product_date', 'product_id', 'created_at'),
        Index('idx_movement_type_date', 'movement_type', 'created_at'),
        Index('idx_movement_reference', 'reference_type', 'reference_id'),
        Index('idx_movement_user_date', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<InventoryMovement(id={self.id}, type='{self.movement_type}', quantity={self.quantity})>"


class InventoryAlert(Base):
    """Modelo de alertas de inventario"""
    __tablename__ = "inventory_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("inventory_lots.id"), nullable=True)
    
    alert_type = Column(String(50), nullable=False)  # 'low_stock', 'expiring_soon', 'expired', 'overstock'
    alert_level = Column(String(20), nullable=False)  # 'info', 'warning', 'critical'
    message = Column(Text, nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    product = relationship("Product")
    lot = relationship("InventoryLot")
    acknowledged_user = relationship("User")
    
    def __repr__(self):
        return f"<InventoryAlert(id={self.id}, type='{self.alert_type}', level='{self.alert_level}')>"


class InventoryCount(Base):
    """Modelo para conteos físicos de inventario"""
    __tablename__ = "inventory_counts"
    
    id = Column(Integer, primary_key=True, index=True)
    count_number = Column(String(50), nullable=False, unique=True)
    count_date = Column(Date, nullable=False)
    location_id = Column(Integer, ForeignKey("inventory_locations.id"), nullable=True)
    
    status = Column(String(20), nullable=False, default='draft')  # draft, in_progress, completed, cancelled
    notes = Column(Text, nullable=True)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    location = relationship("InventoryLocation")
    created_user = relationship("User")
    count_items = relationship("InventoryCountItem", back_populates="count")
    
    def __repr__(self):
        return f"<InventoryCount(id={self.id}, number='{self.count_number}', status='{self.status}')>"


class InventoryCountItem(Base):
    """Modelo para items de conteo físico"""
    __tablename__ = "inventory_count_items"
    
    id = Column(Integer, primary_key=True, index=True)
    count_id = Column(Integer, ForeignKey("inventory_counts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("inventory_lots.id"), nullable=True)
    
    expected_quantity = Column(Integer, nullable=False)
    actual_quantity = Column(Integer, nullable=True)
    variance = Column(Integer, nullable=True)
    variance_percentage = Column(Float, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relaciones
    count = relationship("InventoryCount", back_populates="count_items")
    product = relationship("Product")
    lot = relationship("InventoryLot")
    
    def __repr__(self):
        return f"<InventoryCountItem(id={self.id}, expected={self.expected_quantity}, actual={self.actual_quantity})>" 