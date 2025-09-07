"""
Modelo para configuraciones del sistema
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SystemSettings(Base):
    """Modelo para configuraciones del sistema"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, index=True, nullable=False)
    setting_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemSettings(key='{self.setting_key}', value='{self.setting_value}')>"


# Configuraciones por defecto
DEFAULT_SETTINGS = {
    "cash_register_password": "1234",  # Contraseña por defecto de caja
    "cash_register_name": "Caja Principal",
    "tax_rate": "19.0",  # IVA por defecto
    "currency": "COP",
    "business_name": "Mi Restaurante",
    "business_address": "",
    "business_phone": "",
    "business_email": "",
    "receipt_footer": "¡Gracias por su visita!",
    "auto_backup": "true",
    "session_timeout": "30",  # minutos
    "max_discount": "20.0",  # porcentaje máximo de descuento
    "require_cash_register": "true",  # si requiere caja abierta para ventas
}
