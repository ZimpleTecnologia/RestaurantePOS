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
    ALMACEN = "ALMACEN"
    SUPERVISOR = "SUPERVISOR"


class User(Base):
    """Modelo de Usuario"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MESERO, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    sales = relationship("Sale", back_populates="user")
    inventory_movements = relationship("InventoryMovement", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>" 