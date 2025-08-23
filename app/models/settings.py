"""
Modelo de Configuración del Sistema
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class SystemSettings(Base):
    """Modelo de Configuración del Sistema"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Configuración General
    company_name = Column(String(200), default="Sistema POS")
    currency = Column(String(10), default="USD")
    timezone = Column(String(50), default="UTC-5")
    
    # Configuración de Tema
    primary_color = Column(String(7), default="#667eea")  # Color primario
    secondary_color = Column(String(7), default="#764ba2")  # Color secundario
    accent_color = Column(String(7), default="#28a745")  # Color de acento
    sidebar_color = Column(String(7), default="#667eea")  # Color del sidebar
    
    # Configuración de la Aplicación
    app_title = Column(String(100), default="Sistema POS")
    app_subtitle = Column(String(100), default="Punto de Venta")
    
    # Configuración de Impresión
    print_header = Column(Text, nullable=True)
    print_footer = Column(Text, nullable=True)
    
    # Configuración de Notificaciones
    enable_notifications = Column(Boolean, default=True)
    low_stock_threshold = Column(Integer, default=10)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemSettings(id={self.id}, company='{self.company_name}')>"
