"""
Modelo de Mesa para el sistema POS

DEPRECATED: Este modelo está deprecado. Usar Table de location.py en su lugar.
El modelo Mesa ahora es un alias de Table para backward compatibility.
"""
import warnings
warnings.warn(
    "El modelo 'Mesa' está deprecado. Use 'Table' de 'app.models.location' en su lugar.",
    DeprecationWarning,
    stacklevel=2
)

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Mesa(Base):
    """
    Modelo de Mesa del restaurante - DEPRECATED
    
    Use Table de app.models.location en su lugar.
    Este modelo se mantiene solo para backward compatibility.
    """
    __tablename__ = "mesas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    numero = Column(Integer, nullable=False, unique=True)
    capacidad = Column(Integer, nullable=True)
    estado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Mesa(id={self.id}, numero={self.numero}, nombre='{self.nombre}', estado={'Activo' if self.estado else 'Inactivo'})>"
    
    @property
    def estado_texto(self):
        """Retorna el estado como texto legible"""
        return "Activo" if self.estado else "Inactivo"
