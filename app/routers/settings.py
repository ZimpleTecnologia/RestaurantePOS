"""
Router para Configuración del Sistema
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.settings import SystemSettings
from app.schemas.settings import (
    SystemSettingsCreate,
    SystemSettingsUpdate,
    SystemSettingsResponse,
    CurrencyOption,
    ThemeOption
)

router = APIRouter(prefix="/settings", tags=["settings"])


# Datos predefinidos para monedas y temas
CURRENCIES = [
    CurrencyOption(code="USD", name="Dólar Estadounidense", symbol="$", decimal_places=2),
    CurrencyOption(code="EUR", name="Euro", symbol="€", decimal_places=2),
    CurrencyOption(code="MXN", name="Peso Mexicano", symbol="$", decimal_places=2),
    CurrencyOption(code="COP", name="Peso Colombiano", symbol="$", decimal_places=0),
    CurrencyOption(code="ARS", name="Peso Argentino", symbol="$", decimal_places=2),
    CurrencyOption(code="CLP", name="Peso Chileno", symbol="$", decimal_places=0),
    CurrencyOption(code="PEN", name="Sol Peruano", symbol="S/", decimal_places=2),
    CurrencyOption(code="BRL", name="Real Brasileño", symbol="R$", decimal_places=2),
]

THEMES = [
    ThemeOption(
        name="Azul Clásico",
        primary_color="#667eea",
        secondary_color="#764ba2",
        accent_color="#28a745",
        sidebar_color="#667eea"
    ),
    ThemeOption(
        name="Verde Naturaleza",
        primary_color="#28a745",
        secondary_color="#20c997",
        accent_color="#ffc107",
        sidebar_color="#28a745"
    ),
    ThemeOption(
        name="Naranja Energía",
        primary_color="#fd7e14",
        secondary_color="#e83e8c",
        accent_color="#6f42c1",
        sidebar_color="#fd7e14"
    ),
    ThemeOption(
        name="Rojo Pasión",
        primary_color="#dc3545",
        secondary_color="#fd7e14",
        accent_color="#ffc107",
        sidebar_color="#dc3545"
    ),
    ThemeOption(
        name="Púrpura Elegante",
        primary_color="#6f42c1",
        secondary_color="#e83e8c",
        accent_color="#28a745",
        sidebar_color="#6f42c1"
    ),
]


@router.get("/", response_model=SystemSettingsResponse)
async def get_settings(db: Session = Depends(get_db)):
    """Obtener configuración actual del sistema"""
    settings = db.query(SystemSettings).first()
    if not settings:
        # Crear configuración por defecto si no existe
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/", response_model=SystemSettingsResponse)
async def update_settings(
    settings_update: SystemSettingsUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar configuración del sistema"""
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
    
    # Actualizar solo los campos proporcionados
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    return settings


@router.get("/currencies", response_model=List[CurrencyOption])
async def get_currencies():
    """Obtener lista de monedas disponibles"""
    return CURRENCIES


@router.get("/themes", response_model=List[ThemeOption])
async def get_themes():
    """Obtener lista de temas disponibles"""
    return THEMES


@router.post("/reset", response_model=SystemSettingsResponse)
async def reset_settings(db: Session = Depends(get_db)):
    """Restablecer configuración a valores por defecto"""
    settings = db.query(SystemSettings).first()
    if settings:
        db.delete(settings)
    
    settings = SystemSettings()
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings
