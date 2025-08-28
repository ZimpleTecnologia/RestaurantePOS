"""
Router para configuraciones del sistema
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user
from app.services.settings_service import SettingsService


class SettingUpdate(BaseModel):
    """Modelo para actualizar configuración"""
    value: str
    description: str = None


router = APIRouter(prefix="/settings", tags=["configuración"])


@router.get("/")
def get_all_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener todas las configuraciones del sistema"""
    settings = SettingsService.get_all_settings(db)
    
    # Agregar descripciones para las configuraciones principales
    descriptions = {
        "cash_register_password": "Contraseña para acceso al módulo de caja",
        "cash_register_name": "Nombre de la caja registradora",
        "tax_rate": "Porcentaje de impuestos (IVA)",
        "currency": "Moneda del sistema",
        "business_name": "Nombre del negocio",
        "business_address": "Dirección del negocio",
        "business_phone": "Teléfono del negocio",
        "business_email": "Email del negocio",
        "receipt_footer": "Pie de página para recibos",
        "auto_backup": "Respaldo automático (true/false)",
        "session_timeout": "Tiempo de sesión en minutos",
        "max_discount": "Descuento máximo permitido (%)",
        "require_cash_register": "Requiere caja abierta para ventas (true/false)"
    }
    
    result = []
    for key, value in settings.items():
        result.append({
            "key": key,
            "value": value,
            "description": descriptions.get(key, "Configuración del sistema")
        })
    
    return result


@router.get("/business-info")
def get_business_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener información del negocio"""
    return SettingsService.get_business_info(db)


@router.post("/update")
def update_setting(
    key: str = Form(...),
    value: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar una configuración específica"""
    try:
        setting = SettingsService.set_setting(db, key, value, description)
        
        return {
            "message": "Configuración actualizada exitosamente",
            "setting": {
                "key": setting.setting_key,
                "value": setting.setting_value,
                "description": setting.description
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando configuración: {str(e)}"
        )


@router.post("/change-cash-password")
def change_cash_register_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cambiar contraseña de caja desde configuración"""
    # Verificar contraseña actual
    if not SettingsService.verify_cash_register_password(db, current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    
    # Verificar que las nuevas contraseñas coincidan
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Las contraseñas nuevas no coinciden"
        )
    
    # Verificar longitud mínima
    if len(new_password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 4 caracteres"
        )
    
    try:
        # Cambiar contraseña
        SettingsService.set_cash_register_password(db, new_password)
        
        return {
            "message": "Contraseña de caja cambiada exitosamente",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error cambiando contraseña: {str(e)}"
        )


@router.post("/initialize")
def initialize_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Inicializar configuraciones por defecto"""
    try:
        SettingsService.initialize_default_settings(db)
        
        return {
            "message": "Configuraciones inicializadas exitosamente",
            "settings_count": len(SettingsService.get_all_settings(db))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inicializando configuraciones: {str(e)}"
        )


@router.get("/cash-register-config")
def get_cash_register_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener configuración específica de caja"""
    return {
        "require_cash_register": SettingsService.require_cash_register(db),
        "cash_register_name": SettingsService.get_setting(db, "cash_register_name", "Caja Principal"),
        "has_password": bool(SettingsService.get_cash_register_password(db))
    }
