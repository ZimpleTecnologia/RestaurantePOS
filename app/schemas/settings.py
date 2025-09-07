"""
Esquemas Pydantic para Configuración del Sistema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SystemSettingsBase(BaseModel):
    """Esquema base para configuración del sistema"""
    company_name: str = "Sistema POS"
    currency: str = "USD"
    timezone: str = "UTC-5"
    
    # Configuración de Tema
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    accent_color: str = "#28a745"
    sidebar_color: str = "#667eea"
    
    # Configuración de la Aplicación
    app_title: str = "Sistema POS"
    app_subtitle: str = "Punto de Venta"
    
    # Configuración de Impresión
    print_header: Optional[str] = None
    print_footer: Optional[str] = None
    
    # Configuración de Notificaciones
    enable_notifications: bool = True
    low_stock_threshold: int = 10


class SystemSettingsCreate(SystemSettingsBase):
    """Esquema para crear configuración"""
    pass


class SystemSettingsUpdate(BaseModel):
    """Esquema para actualizar configuración"""
    company_name: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    sidebar_color: Optional[str] = None
    app_title: Optional[str] = None
    app_subtitle: Optional[str] = None
    print_header: Optional[str] = None
    print_footer: Optional[str] = None
    enable_notifications: Optional[bool] = None
    low_stock_threshold: Optional[int] = None


class SystemSettingsResponse(SystemSettingsBase):
    """Esquema de respuesta para configuración"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CurrencyOption(BaseModel):
    """Esquema para opciones de moneda"""
    code: str
    name: str
    symbol: str
    decimal_places: int = 2


class ThemeOption(BaseModel):
    """Esquema para opciones de tema"""
    name: str
    primary_color: str
    secondary_color: str
    accent_color: str
    sidebar_color: str
