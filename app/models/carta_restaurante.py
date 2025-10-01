"""
Modelos para el sistema de Carta Restaurante
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from decimal import Decimal


class TipoPlato(str, enum.Enum):
    """Tipos de platos en la carta"""
    FIJO = "Fijo"
    VARIABLE = "Variable"


class CategoriaPlato(str, enum.Enum):
    """Categorías de platos"""
    ENTRADA = "Entrada"
    PLATO_PRINCIPAL = "Plato Principal"
    ACOMPANAMIENTO = "Acompañamiento"
    BEBIDA = "Bebida"
    POSTRE = "Postre"
    OTRO = "Otro"


class CartaRestaurante(Base):
    """Modelo para la carta del restaurante"""
    __tablename__ = "carta_restaurante"
    
    producto_id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_base = Column(Numeric(10, 2), nullable=False)
    tipo = Column(Enum(TipoPlato), nullable=False)
    activo = Column(Boolean, default=True)
    categoria = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    menu_opciones = relationship("app.models.carta_restaurante.MenuOpcion", back_populates="producto")
    order_items = relationship("app.models.order.OrderItem", back_populates="carta_producto")
    
    def __repr__(self):
        return f"<CartaRestaurante(id={self.producto_id}, nombre='{self.nombre}', tipo='{self.tipo}')>"
    
    @property
    def is_fijo(self):
        """Verificar si es un plato fijo"""
        return self.tipo == TipoPlato.FIJO
    
    @property
    def is_variable(self):
        """Verificar si es un plato variable"""
        return self.tipo == TipoPlato.VARIABLE


class MenuDia(Base):
    """Modelo para el menú del día"""
    __tablename__ = "menus_dia_carta"
    
    menu_id = Column(Integer, primary_key=True)
    fecha = Column(String(10), nullable=False, unique=True)  # YYYY-MM-DD
    nombre = Column(String(100), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    menu_opciones = relationship("app.models.carta_restaurante.MenuOpcion", back_populates="menu", cascade="all, delete-orphan")
    order_items = relationship("app.models.order.OrderItem", back_populates="menu")
    
    def __repr__(self):
        return f"<MenuDia(id={self.menu_id}, fecha='{self.fecha}', nombre='{self.nombre}')>"
    
    @property
    def is_active(self):
        """Verificar si el menú está activo"""
        return self.activo
    
    def get_platos_fijos(self):
        """Obtener platos fijos del menú"""
        return [opcion for opcion in self.menu_opciones if opcion.es_fijo]
    
    def get_platos_variables(self):
        """Obtener platos variables del menú"""
        return [opcion for opcion in self.menu_opciones if not opcion.es_fijo]
    
    def get_platos_por_categoria(self, categoria):
        """Obtener platos de una categoría específica"""
        return [opcion for opcion in self.menu_opciones if opcion.producto.categoria == categoria]


class MenuOpcion(Base):
    """Modelo para las opciones del menú del día"""
    __tablename__ = "menu_opciones"
    
    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, ForeignKey("menus_dia_carta.menu_id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("carta_restaurante.producto_id"), nullable=False)
    es_fijo = Column(Boolean, nullable=False)
    orden = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    menu = relationship("app.models.carta_restaurante.MenuDia", back_populates="menu_opciones")
    producto = relationship("app.models.carta_restaurante.CartaRestaurante", back_populates="menu_opciones")
    
    def __repr__(self):
        return f"<MenuOpcion(id={self.id}, menu_id={self.menu_id}, producto_id={self.producto_id}, es_fijo={self.es_fijo})>"
