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
    """Estados de mesa"""
    LIBRE = "libre"
    OCUPADA = "ocupada"
    RESERVADA = "reservada"
    MANTENIMIENTO = "mantenimiento"


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
    
    # Relaciones
    tables = relationship("Table", back_populates="location")
    
    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', type='{self.location_type}')>"


class Table(Base):
    """Modelo de Mesa - Simplificado"""
    __tablename__ = "tables"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    table_number = Column(String(20), nullable=False)
    name = Column(String(100), nullable=True)
    capacity = Column(Integer, default=4)
    status = Column(Enum(TableStatus), default=TableStatus.LIBRE)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    location = relationship("Location", back_populates="tables")
    orders = relationship("Order", back_populates="table")
    
    def __repr__(self):
        return f"<Table(id={self.id}, number='{self.table_number}', status='{self.status}')>" 