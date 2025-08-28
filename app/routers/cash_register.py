"""
Módulo Unificado de Caja - Con Autenticación y Protección
"""
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.cash_register import CashRegister, CashSession, CashMovement, CashStatus, MovementType
from app.auth.dependencies import get_current_active_user
from app.services.cash_service import CashService
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/cash-register", tags=["caja"])


# ============================================================================
# AUTENTICACIÓN DE CAJA
# ============================================================================

@router.post("/auth")
def authenticate_cash_register(
    password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Autenticar acceso al módulo de caja"""
    if not SettingsService.verify_cash_register_password(db, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña de caja incorrecta"
        )
    
    return {
        "message": "Autenticación exitosa",
        "user": current_user.full_name,
        "timestamp": datetime.now()
    }


# ============================================================================
# ESTADO Y CONTROL DE CAJA
# ============================================================================

@router.get("/registers")
def get_cash_registers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener todas las cajas registradoras"""
    cash_registers = db.query(CashRegister).filter(CashRegister.is_active == True).all()
    
    result = []
    for register in cash_registers:
        # Obtener sesión activa para cada caja
        active_session = CashService.get_active_session(db, register.id)
        
        register_data = {
            "id": register.id,
            "name": register.name,
            "register_number": register.register_number,
            "description": register.description,
            "is_active": register.is_active,
            "created_at": register.created_at,
            "has_active_session": active_session is not None,
            "active_session": {
                "id": active_session.id,
                "session_number": active_session.session_number,
                "opened_at": active_session.opened_at,
                "opening_amount": active_session.opening_amount,
                "user_name": active_session.user.full_name
            } if active_session else None
        }
        result.append(register_data)
    
    return result


@router.get("/status")
def get_cash_register_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estado completo de la caja"""
    # Verificar que existe la caja principal
    cash_register = CashService.get_main_cash_register(db)
    if not cash_register:
        cash_register = CashService.create_main_cash_register(db)
    
    # Obtener sesión activa
    active_session = CashService.get_active_session(db, cash_register.id)
    today_session = CashService.get_today_session(db, cash_register.id)
    
    # Obtener información del negocio
    business_info = SettingsService.get_business_info(db)
    
    return {
        "cash_register": {
            "id": cash_register.id,
            "name": cash_register.name,
            "register_number": cash_register.register_number
        },
        "business_info": business_info,
        "has_active_session": active_session is not None,
        "has_today_session": today_session is not None,
        "can_create_sales": active_session is not None,
        "require_cash_register": SettingsService.require_cash_register(db),
        "active_session": {
            "id": active_session.id,
            "session_number": active_session.session_number,
            "opened_at": active_session.opened_at,
            "opening_amount": active_session.opening_amount,
            "opening_notes": active_session.opening_notes,
            "user_name": active_session.user.full_name,
            "total_sales": active_session.total_sales,
            "total_expenses": active_session.total_expenses,
            "expected_amount": active_session.expected_amount
        } if active_session else None,
        "today_session": {
            "id": today_session.id,
            "session_number": today_session.session_number,
            "status": today_session.status,
            "opened_at": today_session.opened_at,
            "closed_at": today_session.closed_at,
            "opening_amount": today_session.opening_amount,
            "closing_amount": today_session.closing_amount,
            "user_name": today_session.user.full_name
        } if today_session else None
    }


# ============================================================================
# APERTURA Y CIERRE DE CAJA
# ============================================================================

@router.post("/open")
def open_cash_register(
    password: str = Form(...),
    opening_amount: Decimal = Form(0),
    opening_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Abrir caja registradora - Requiere autenticación"""
    # Verificar contraseña
    if not SettingsService.verify_cash_register_password(db, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña de caja incorrecta"
        )
    
    try:
        # Obtener o crear caja principal
        cash_register = CashService.get_main_cash_register(db)
        if not cash_register:
            cash_register = CashService.create_main_cash_register(db)
        
        # Abrir sesión
        session = CashService.open_session(
            db=db,
            cash_register_id=cash_register.id,
        user_id=current_user.id,
            opening_amount=opening_amount,
            opening_notes=opening_notes
        )
        
        return {
            "message": "Caja abierta exitosamente",
            "session": {
                "id": session.id,
                "session_number": session.session_number,
                "opened_at": session.opened_at,
                "opening_amount": session.opening_amount,
                "user_name": session.user.full_name
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error abriendo caja: {str(e)}")


@router.post("/close")
def close_cash_register(
    password: str = Form(...),
    closing_amount: Decimal = Form(...),
    closing_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cerrar caja registradora - Requiere autenticación"""
    # Verificar contraseña
    if not SettingsService.verify_cash_register_password(db, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña de caja incorrecta"
        )
    
    try:
        # Obtener caja principal
        cash_register = CashService.get_main_cash_register(db)
        if not cash_register:
            raise HTTPException(status_code=404, detail="No hay caja registrada")
        
        # Obtener sesión activa
        active_session = CashService.get_active_session(db, cash_register.id)
        if not active_session:
            raise HTTPException(status_code=400, detail="No hay sesión activa para cerrar")
        
        # Cerrar sesión
        session = CashService.close_session(
            db=db,
            session_id=active_session.id,
            closing_amount=closing_amount,
            closing_notes=closing_notes
        )
        
        # Obtener resumen final
        summary = CashService.get_session_summary(db, session.id)
        
        return {
            "message": "Caja cerrada exitosamente",
            "session": {
                "id": session.id,
                "session_number": session.session_number,
                "closed_at": session.closed_at,
                "closing_amount": session.closing_amount,
                "user_name": session.user.full_name
            },
            "summary": summary
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cerrando caja: {str(e)}")


# ============================================================================
# REPORTES Y CONSULTAS
# ============================================================================

@router.get("/sessions")
def get_cash_sessions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener historial de sesiones de caja"""
    cash_register = CashService.get_main_cash_register(db)
    if not cash_register:
        return []
    
    sessions = db.query(CashSession).filter(
        CashSession.cash_register_id == cash_register.id
    ).order_by(CashSession.opened_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for session in sessions:
        session_data = {
            "id": session.id,
            "session_number": session.session_number,
            "opened_at": session.opened_at,
            "closed_at": session.closed_at,
            "opening_amount": session.opening_amount,
            "closing_amount": session.closing_amount,
            "status": session.status,
            "user_name": session.user.full_name,
            "total_sales": session.total_sales,
            "total_expenses": session.total_expenses,
            "expected_amount": session.expected_amount
        }
        result.append(session_data)
    
    return result


@router.get("/sessions/{session_id}")
def get_cash_session_detail(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener detalles de una sesión de caja"""
    summary = CashService.get_session_summary(db, session_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    return summary


@router.get("/report/daily")
def get_daily_cash_report(
    report_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte diario de caja"""
    return CashService.get_daily_report(db, report_date)


@router.get("/movements")
def get_cash_movements(
    session_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener movimientos de caja"""
    query = db.query(CashMovement)
    
    if session_id:
        query = query.filter(CashMovement.session_id == session_id)
    else:
        # Si no se especifica sesión, obtener movimientos de la sesión activa
        cash_register = CashService.get_main_cash_register(db)
        if cash_register:
            active_session = CashService.get_active_session(db, cash_register.id)
            if active_session:
                query = query.filter(CashMovement.session_id == active_session.id)
    
    movements = query.order_by(CashMovement.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for movement in movements:
        movement_data = {
            "id": movement.id,
            "movement_type": movement.movement_type,
            "amount": movement.amount,
            "description": movement.description,
            "reference": movement.reference,
            "notes": movement.notes,
            "created_at": movement.created_at,
            "session_number": movement.session.session_number
        }
        result.append(movement_data)
    
    return result


# ============================================================================
# CONFIGURACIÓN DE CAJA
# ============================================================================

@router.post("/change-password")
def change_cash_register_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cambiar contraseña de caja"""
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
