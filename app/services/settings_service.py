"""
Servicio para manejo de configuraciones del sistema
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.settings import SystemSettings, DEFAULT_SETTINGS


class SettingsService:
    """Servicio para manejo de configuraciones"""
    
    @staticmethod
    def get_setting(db: Session, key: str, default: str = None) -> str:
        """Obtener una configuración específica"""
        setting = db.query(SystemSettings).filter(
            SystemSettings.setting_key == key,
            SystemSettings.is_active == True
        ).first()
        
        if setting:
            return setting.setting_value
        return default
    
    @staticmethod
    def set_setting(db: Session, key: str, value: str, description: str = None) -> SystemSettings:
        """Establecer una configuración"""
        setting = db.query(SystemSettings).filter(
            SystemSettings.setting_key == key
        ).first()
        
        if setting:
            setting.setting_value = value
            if description:
                setting.description = description
        else:
            setting = SystemSettings(
                setting_key=key,
                setting_value=value,
                description=description
            )
            db.add(setting)
        
        db.commit()
        db.refresh(setting)
        return setting
    
    @staticmethod
    def get_all_settings(db: Session) -> Dict[str, str]:
        """Obtener todas las configuraciones como diccionario"""
        settings = db.query(SystemSettings).filter(
            SystemSettings.is_active == True
        ).all()
        
        result = {}
        for setting in settings:
            result[setting.setting_key] = setting.setting_value
        
        return result
    
    @staticmethod
    def initialize_default_settings(db: Session) -> None:
        """Inicializar configuraciones por defecto"""
        for key, value in DEFAULT_SETTINGS.items():
            existing = db.query(SystemSettings).filter(
                SystemSettings.setting_key == key
            ).first()
            
            if not existing:
                setting = SystemSettings(
                    setting_key=key,
                    setting_value=value,
                    description=f"Configuración por defecto: {key}"
                )
                db.add(setting)
        
        db.commit()
    
    @staticmethod
    def get_cash_register_password(db: Session) -> str:
        """Obtener contraseña de caja"""
        return SettingsService.get_setting(db, "cash_register_password", "1234")
    
    @staticmethod
    def set_cash_register_password(db: Session, password: str) -> SystemSettings:
        """Cambiar contraseña de caja"""
        return SettingsService.set_setting(
            db, 
            "cash_register_password", 
            password, 
            "Contraseña para acceso al módulo de caja"
        )
    
    @staticmethod
    def verify_cash_register_password(db: Session, password: str) -> bool:
        """Verificar contraseña de caja"""
        stored_password = SettingsService.get_cash_register_password(db)
        return password == stored_password
    
    @staticmethod
    def get_business_info(db: Session) -> Dict[str, str]:
        """Obtener información del negocio"""
        return {
            "name": SettingsService.get_setting(db, "business_name", "Mi Restaurante"),
            "address": SettingsService.get_setting(db, "business_address", ""),
            "phone": SettingsService.get_setting(db, "business_phone", ""),
            "email": SettingsService.get_setting(db, "business_email", ""),
            "currency": SettingsService.get_setting(db, "currency", "COP"),
            "tax_rate": SettingsService.get_setting(db, "tax_rate", "19.0"),
        }
    
    @staticmethod
    def require_cash_register(db: Session) -> bool:
        """Verificar si se requiere caja abierta para ventas"""
        value = SettingsService.get_setting(db, "require_cash_register", "true")
        return value.lower() == "true"
