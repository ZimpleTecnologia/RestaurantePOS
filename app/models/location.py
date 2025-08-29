"""
Modelos de Ubicaciones y Mesas - Simplificados
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class LocationType(str, enum.Enum):
    """Tipos de ubicación"""
    RESTAURANTE = "restaurante"
    BAR = "bar"
    LAVADERO = "lavadero"
    TIENDA = "tienda"
    OFICINA = "oficina"
    OTRO = "otro"


class TableStatus(str, enum.Enum):
    """Estados de las mesas"""
    AVAILABLE = "disponible"      # Mesa libre
    OCCUPIED = "ocupada"          # Mesa con clientes
    RESERVED = "reservada"        # Mesa reservada
    CLEANING = "limpieza"         # Mesa en limpieza
    OUT_OF_SERVICE = "fuera_de_servicio"  # Mesa fuera de servicio
    
    # Alias para compatibilidad
    LIBRE = "disponible"
    OCUPADA = "ocupada"
    RESERVADA = "reservada"
    MANTENIMIENTO = "fuera_de_servicio"


class Location(Base):
    """Modelo de Ubicación - Simplificado"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    location_type = Column(Enum(LocationType), default=LocationType.RESTAURANTE)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    manager_name = Column(String(100), nullable=True)
    capacity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones - Comentamos esta relación ya que Table ya no tiene location_id
    # tables = relationship("Table", back_populates="location")
    
    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', type='{self.location_type}')>"


class Table(Base):
    """Modelo para las mesas del restaurante"""
    __tablename__ = "restaurant_tables"
    
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)  # Ej: "Mesa 1", "Terraza 3"
    capacity = Column(Integer, nullable=False, default=4)  # Capacidad de personas
    status = Column(Enum(TableStatus, values_callable=lambda obj: [e.value for e in obj]), default=TableStatus.AVAILABLE)
    location = Column(String(50), nullable=True)  # Ej: "Interior", "Terraza", "Bar"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    orders = relationship("Order", back_populates="table")
    
    def __repr__(self):
        return f"<Table(id={self.id}, number='{self.table_number}', status='{self.status}')>"
    
    @property
    def is_available(self):
        """Verificar si la mesa está disponible"""
        return self.status == TableStatus.AVAILABLE
    
    @property
    def has_active_order(self):
        """Verificar si la mesa tiene un pedido activo"""
        return any(order.is_active for order in self.orders)
    
    @property
    def current_order(self):
        """Obtener el pedido activo actual"""
        for order in self.orders:
            if order.is_active:
                return order
        return None 