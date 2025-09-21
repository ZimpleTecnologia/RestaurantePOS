"""
Modelos para el sistema de menús reestructurado
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, Date, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class CategoriaPlatoVariable(Base):
    """Categorías de platos variables (Principio, Proteína, etc.)"""
    __tablename__ = "categorias_platos_variables"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    opciones = relationship("OpcionPlato", back_populates="categoria")
    
    def __repr__(self):
        return f"<CategoriaPlatoVariable(id={self.id}, nombre='{self.nombre}')>"

class OpcionPlato(Base):
    """Opciones de platos (fijos y variables)"""
    __tablename__ = "opciones_platos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias_platos_variables.id"), nullable=True)
    tipo = Column(String(20), nullable=False)  # 'Fijo' o 'Variable'
    precio = Column(Numeric(10, 2), default=0.00)
    imagen_url = Column(String(255), nullable=True)
    imagen_data = Column(LargeBinary, nullable=True)  # Imagen como BLOB
    imagen_tipo = Column(String(50), nullable=True)  # Tipo MIME de la imagen
    activo = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones - usando foreign_keys explícitas
    categoria = relationship("CategoriaPlatoVariable", back_populates="opciones", foreign_keys=[categoria_id])
    menu_opciones = relationship("MenuDiaOpcion", back_populates="opcion", foreign_keys="MenuDiaOpcion.opcion_id")
    
    def __repr__(self):
        return f"<OpcionPlato(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}')>"
    
    @property
    def es_fijo(self):
        return self.tipo == 'Fijo'
    
    @property
    def es_variable(self):
        return self.tipo == 'Variable'

class MenuDiaOpcion(Base):
    """Relación entre menús del día y opciones de platos"""
    __tablename__ = "menu_dia_opciones"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    menu_dia_id = Column(Integer, ForeignKey("menus_dia.id"), nullable=False)
    opcion_id = Column(Integer, ForeignKey("opciones_platos.id"), nullable=False)
    disponible = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones - usando foreign_keys explícitas
    menu_dia = relationship("MenuDiaRestructured", back_populates="opciones", foreign_keys=[menu_dia_id])
    opcion = relationship("OpcionPlato", back_populates="menu_opciones", foreign_keys=[opcion_id])
    
    def __repr__(self):
        return f"<MenuDiaOpcion(menu_dia_id={self.menu_dia_id}, opcion_id={self.opcion_id})>"

# Modelo MenuDia para el sistema reestructurado
class MenuDiaRestructured(Base):
    """Menú del día con opciones"""
    __tablename__ = "menus_dia"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, unique=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False, default=0.00)
    estado = Column(String(50), nullable=True)  # ENUM: 'ACTIVE', 'INACTIVE', 'DRAFT'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones - usando foreign_keys explícitas
    opciones = relationship("MenuDiaOpcion", back_populates="menu_dia", foreign_keys="MenuDiaOpcion.menu_dia_id")
    
    def __repr__(self):
        return f"<MenuDiaRestructured(id={self.id}, fecha='{self.fecha}', estado='{self.estado}')>"
    
    def get_platos_fijos(self):
        """Obtener platos fijos del menú"""
        return [op.menu_dia for op in self.opciones if op.opcion.es_fijo and op.disponible]
    
    def get_platos_variables(self):
        """Obtener platos variables del menú organizados por categoría"""
        categorias = {}
        for op in self.opciones:
            if op.opcion.es_variable and op.disponible:
                categoria_nombre = op.opcion.categoria.nombre if op.opcion.categoria else 'Sin categoría'
                if categoria_nombre not in categorias:
                    categorias[categoria_nombre] = []
                categorias[categoria_nombre].append(op.opcion)
        return categorias
