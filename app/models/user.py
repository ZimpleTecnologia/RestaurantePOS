"""
Modelo de Usuario para el sistema POS
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """Roles de usuario en el sistema de restaurante"""
    ADMIN = "ADMIN"
    MESERO = "MESERO"
    COCINA = "COCINA"
    CAJA = "CAJA"


class User(Base):
    """Modelo de Usuario"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)  # Campo añadido
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MESERO, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones existentes
    sales = relationship("Sale", back_populates="user")
    inventory_movements = relationship("InventoryMovement", back_populates="user")
    
    # Nueva relación muchos-a-muchos con permisos
    permisos = relationship(
        "Permiso",
        secondary="usuario_permiso",
        back_populates="usuarios",
        lazy="selectin"  # Carga automática de permisos
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    def tiene_permiso(self, codigo_permiso: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico
        Los ADMIN tienen todos los permisos por defecto
        """
        if self.role == UserRole.ADMIN:
            return True
        return any(p.codigo == codigo_permiso and p.estado for p in self.permisos) 