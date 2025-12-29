"""
Modelo de Mesa para el sistema POS
Gestión de mesas del restaurante
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Mesa(Base):
    """
    Modelo de Mesa del restaurante
    
    Attributes:
        id: Identificador único de la mesa
        nombre: Nombre descriptivo de la mesa (ej: "Mesa 1", "Terraza A")
        numero: Número de la mesa
        capacidad: Capacidad máxima de personas (opcional)
        estado: Estado de la mesa (activo/inactivo)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """
    __tablename__ = "mesas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    numero = Column(Integer, nullable=False, unique=True)
    capacidad = Column(Integer, nullable=True)
    estado = Column(Boolean, default=True, nullable=False)  # True = activo, False = inactivo
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones (para futuro: pedidos asociados a mesas)
    # orders = relationship("Order", back_populates="mesa")
    
    def __repr__(self):
        return f"<Mesa(id={self.id}, numero={self.numero}, nombre='{self.nombre}', estado={'Activo' if self.estado else 'Inactivo'})>"
    
    @property
    def estado_texto(self):
        """Retorna el estado como texto legible"""
        return "Activo" if self.estado else "Inactivo"

