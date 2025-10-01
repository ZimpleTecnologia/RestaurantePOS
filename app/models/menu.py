"""
Modelos para el sistema de menú del día
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
from decimal import Decimal


class MenuStatus(str, enum.Enum):
    """Estados del menú del día"""
    ACTIVE = "activo"
    INACTIVE = "inactivo"
    DRAFT = "borrador"


class MenuDayOld(Base):
    """Modelo para el menú del día (sistema anterior)"""
    __tablename__ = "menus_dia"
    
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    estado = Column(Enum(MenuStatus), default=MenuStatus.ACTIVE)
    descripcion = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    opciones = relationship("OpcionMenu", back_populates="menu", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="menu_old", foreign_keys="OrderItem.menu_id_old")
    
    def __repr__(self):
        return f"<MenuDayOld(id={self.id}, fecha='{self.fecha}', nombre='{self.nombre}')>"
    
    @property
    def is_active(self):
        """Verificar si el menú está activo"""
        return self.estado == MenuStatus.ACTIVE
    
    def get_opciones_por_categoria(self):
        """Obtener opciones agrupadas por categoría"""
        categorias = {}
        for opcion in self.opciones:
            if opcion.categoria.nombre not in categorias:
                categorias[opcion.categoria.nombre] = {
                    'categoria': opcion.categoria,
                    'opciones': []
                }
            categorias[opcion.categoria.nombre]['opciones'].append(opcion)
        return categorias


class CategoriaMenu(Base):
    """Modelo para categorías del menú"""
    __tablename__ = "categorias_menu"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)
    orden = Column(Integer, nullable=False, default=0)
    descripcion = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    opciones = relationship("OpcionMenu", back_populates="categoria")
    order_items = relationship("OrderItem", back_populates="categoria")
    
    def __repr__(self):
        return f"<CategoriaMenu(id={self.id}, nombre='{self.nombre}', orden={self.orden})>"


class OpcionMenu(Base):
    """Modelo para opciones del menú"""
    __tablename__ = "opciones_menu"
    
    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, ForeignKey("menus_dia.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias_menu.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    menu = relationship("MenuDayOld", back_populates="opciones")
    categoria = relationship("CategoriaMenu", back_populates="opciones")
    order_items = relationship("OrderItem", back_populates="opcion")
    
    def __repr__(self):
        return f"<OpcionMenu(id={self.id}, nombre='{self.nombre}', categoria='{self.categoria.nombre}')>"


