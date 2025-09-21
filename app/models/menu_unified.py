"""
Modelo unificado para el sistema de Gestión de Menús
"""
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date


# Tabla intermedia para la relación many-to-many entre Menu y Plato
menu_platos = Table(
    'menu_platos',
    Base.metadata,
    Column('menu_id', Integer, ForeignKey('menus.id'), primary_key=True),
    Column('plato_id', Integer, ForeignKey('platos.id'), primary_key=True)
)


class Menu(Base):
    """Modelo unificado para menús del día"""
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, unique=True, index=True)
    activo = Column(Boolean, default=True)
    nombre = Column(String(100), nullable=True)  # Nombre opcional del menú
    descripcion = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación many-to-many con platos
    platos = relationship("Plato", secondary=menu_platos, back_populates="menus")
    
    def __repr__(self):
        return f"<Menu(id={self.id}, fecha='{self.fecha}', activo={self.activo})>"
    
    @property
    def is_active(self):
        """Verificar si el menú está activo"""
        return self.activo
    
    def get_platos_fijos(self):
        """Obtener platos fijos del menú"""
        return [plato for plato in self.platos if plato.tipo == 'Fijo']
    
    def get_platos_variables(self):
        """Obtener platos variables del menú"""
        return [plato for plato in self.platos if plato.tipo == 'Variable']


class Plato(Base):
    """Modelo simplificado para platos"""
    __tablename__ = "platos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(String(20), nullable=False)  # Precio como string para flexibilidad
    tipo = Column(String(20), nullable=False)  # 'Fijo' o 'Variable'
    categoria = Column(String(50), nullable=True)
    activo = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación many-to-many con menús
    menus = relationship("Menu", secondary=menu_platos, back_populates="platos")
    
    def __repr__(self):
        return f"<Plato(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}')>"
    
    @property
    def is_fijo(self):
        """Verificar si es un plato fijo"""
        return self.tipo == 'Fijo'
    
    @property
    def is_variable(self):
        """Verificar si es un plato variable"""
        return self.tipo == 'Variable'


