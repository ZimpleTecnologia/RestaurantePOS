"""
Modelos de Permisos para el sistema POS
Sistema de control de acceso basado en permisos
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


# Tabla intermedia para la relación muchos-a-muchos entre Usuario y Permiso
usuario_permiso = Table(
    'usuario_permiso',
    Base.metadata,
    Column('usuario_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('permiso_id', Integer, ForeignKey('permisos.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)


class Permiso(Base):
    """
    Modelo de Permiso del sistema
    
    Define los diferentes permisos que pueden ser asignados a usuarios.
    Cada permiso controla el acceso a un módulo o funcionalidad específica.
    
    Attributes:
        id: Identificador único del permiso
        codigo: Código único del permiso (ej: "mesas", "usuarios", "cocina")
        nombre: Nombre descriptivo del permiso
        descripcion: Descripción detallada de qué permite este permiso
        modulo: Módulo al que pertenece el permiso
        estado: Estado del permiso (activo/inactivo)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """
    __tablename__ = "permisos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    modulo = Column(String(50), nullable=False)  # ej: "administracion", "ventas", "cocina"
    estado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación muchos-a-muchos con usuarios
    usuarios = relationship(
        "User",
        secondary=usuario_permiso,
        back_populates="permisos"
    )
    
    def __repr__(self):
        return f"<Permiso(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"
    
    @property
    def estado_texto(self):
        """Retorna el estado como texto legible"""
        return "Activo" if self.estado else "Inactivo"

