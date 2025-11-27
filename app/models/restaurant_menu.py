"""
Modelos para el sistema de menús del restaurante
Estructura: Menú del día con categorías (principio, proteína) + platos fijos + acompañamientos fijos
"""
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Text, ForeignKey, Table, Numeric, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date


# Tabla intermedia para menú del día con categorías
menu_categoria_platos = Table(
    'menu_categoria_platos',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('menu_dia_id', Integer, ForeignKey('menus_dia.id'), nullable=False),
    Column('categoria_id', Integer, ForeignKey('categorias_menu.id'), nullable=False),
    Column('plato_id', Integer, ForeignKey('platos_restaurante.id'), nullable=False),
    Column('activo', Boolean, default=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)


class CategoriaMenuRestaurante(Base):
    """Categorías de platos para el menú del día (Principio, Proteína, etc.)"""
    __tablename__ = "categorias_menu"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)  # "Principio", "Proteína", etc.
    descripcion = Column(Text, nullable=True)
    orden = Column(Integer, default=0)  # Para ordenar las categorías
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones (temporalmente comentada para evitar errores)
    # menu_platos = relationship("MenuCategoriaPlato", back_populates="categoria")
    
    def __repr__(self):
        return f"<CategoriaMenuRestaurante(id={self.id}, nombre='{self.nombre}')>"


class PlatoRestaurante(Base):
    """Platos del restaurante (tanto para menú del día como platos fijos)"""
    __tablename__ = "platos_restaurante"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False, default=0.0)
    tipo = Column(String(20), nullable=False)  # 'Menu_Dia', 'Plato_Fijo', 'Acompanamiento_Fijo'
    activo = Column(Boolean, default=True)
    
    # Categoría sugerida por defecto (opcional, solo para platos de tipo Menu_Dia)
    categoria_id = Column(Integer, ForeignKey('categorias_menu.id'), nullable=True)
    
    # Campos de imagen (similar al modelo OpcionPlato)
    imagen_data = Column(LargeBinary, nullable=True)  # Imagen como BLOB
    imagen_tipo = Column(String(50), nullable=True)  # Tipo MIME de la imagen
    
    # Relación con categoría
    categoria = relationship("CategoriaMenuRestaurante", foreign_keys=[categoria_id])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones (temporalmente comentada para evitar errores)
    # menu_platos = relationship("MenuCategoriaPlato", back_populates="plato")
    # pedidos_items = relationship("OrderItem", back_populates="plato_restaurante")
    
    def __repr__(self):
        return f"<PlatoRestaurante(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}')>"
    
    @property
    def is_menu_dia(self):
        return self.tipo == 'Menu_Dia'
    
    @property
    def is_plato_fijo(self):
        return self.tipo == 'Plato_Fijo'
    
    @property
    def is_acompanamiento_fijo(self):
        return self.tipo == 'Acompanamiento_Fijo'


class MenuDia(Base):
    """Menú del día con categorías de opciones"""
    __tablename__ = "menus_dia"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)  # Usar id (renombrado de menu_id)
    fecha = Column(Date, nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)  # "Almuerzo del 18/09/2025"
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False, default=0.00)
    estado = Column(String(50), nullable=True)  # ENUM: 'ACTIVE', 'INACTIVE', 'DRAFT'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones (temporalmente comentada para evitar errores)
    # categorias_platos = relationship("MenuCategoriaPlato", back_populates="menu_dia")
    # pedidos = relationship("Order", back_populates="menu_dia")
    
    def __repr__(self):
        return f"<MenuDia(id={self.id}, fecha='{self.fecha}', publicado={self.publicado})>"
    
    def get_platos_por_categoria(self, categoria_nombre):
        """Obtener platos de una categoría específica"""
        return [
            mcp.plato for mcp in self.categorias_platos 
            if mcp.categoria.nombre == categoria_nombre and mcp.activo
        ]
    
    def get_principios(self):
        """Obtener platos de principio"""
        return self.get_platos_por_categoria("Principio")
    
    def get_proteinas(self):
        """Obtener platos de proteína"""
        return self.get_platos_por_categoria("Proteína")


class MenuCategoriaPlato(Base):
    """Relación entre menú del día, categoría y plato"""
    __tablename__ = "menu_categoria_platos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    menu_dia_id = Column(Integer, ForeignKey('menus_dia.id'), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias_menu.id'), nullable=False)
    plato_id = Column(Integer, ForeignKey('platos_restaurante.id'), nullable=False)
    activo = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones (temporalmente comentada para evitar errores)
    # menu_dia = relationship("MenuDia", back_populates="categorias_platos")
    # categoria = relationship("CategoriaMenuRestaurante", back_populates="menu_platos")
    # plato = relationship("PlatoRestaurante", back_populates="menu_platos")
    
    def __repr__(self):
        return f"<MenuCategoriaPlato(menu_dia_id={self.menu_dia_id}, categoria='{self.categoria.nombre}', plato='{self.plato.nombre}')>"


class AcompanamientoFijo(Base):
    """Acompañamientos que siempre se incluyen en el almuerzo"""
    __tablename__ = "acompanamientos_fijos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    orden = Column(Integer, default=0)  # Para ordenar en la vista
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<AcompanamientoFijo(id={self.id}, nombre='{self.nombre}')>"
