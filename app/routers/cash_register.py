"""
Router para el sistema de caja
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.database import get_db
from app.models.user import User
from app.models.cash_register import (
    CashRegister, CashSession, CashMovement, 
    CASH_REGISTER_STATUS, CASH_MOVEMENT_TYPE
)
from app.auth.dependencies import get_current_active_user
from app.schemas.cash_register import (
    CashRegisterCreate, CashRegisterUpdate, CashRegisterResponse,
    CashSessionCreate, CashSessionClose, CashSessionResponse,
    CashMovementCreate, CashMovementResponse,
    CashSessionSummary, CashRegisterReport
)

router = APIRouter(prefix="/cash-register", tags=["caja"])


def generate_session_number(db: Session, cash_register_id: int) -> str:
    """Generar número único de sesión"""
    today = date.today()
    prefix = f"S{today.strftime('%Y%m%d')}"
    
    # Contar sesiones del día para esta caja
    count = db.query(func.count(CashSession.id)).filter(
        and_(
            func.date(CashSession.opened_at) == today,
            CashSession.cash_register_id == cash_register_id
        )
    ).scalar()
    
    return f"{prefix}-{cash_register_id:02d}-{count + 1:04d}"


# Endpoints para CashRegister
@router.get("/registers", response_model=List[CashRegisterResponse])
def get_cash_registers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de cajas registradoras"""
    registers = db.query(CashRegister).filter(CashRegister.is_active == True).all()
    return registers


@router.post("/registers", response_model=CashRegisterResponse)
def create_cash_register(
    register_data: CashRegisterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nueva caja registradora"""
    # Verificar que el número de caja no exista
    existing = db.query(CashRegister).filter(
        CashRegister.register_number == register_data.register_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Ya existe una caja con ese número"
        )
    
    db_register = CashRegister(**register_data.dict())
    db.add(db_register)
    db.commit()
    db.refresh(db_register)
    return db_register


@router.get("/registers/{register_id}", response_model=CashRegisterResponse)
def get_cash_register(
    register_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener caja registradora por ID"""
    register = db.query(CashRegister).filter(CashRegister.id == register_id).first()
    if not register:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    return register


# Endpoints para CashSession
@router.get("/sessions", response_model=List[CashSessionResponse])
def get_cash_sessions(
    skip: int = 0,
    limit: int = 100,
    register_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de sesiones de caja"""
    query = db.query(CashSession)
    
    if register_id:
        query = query.filter(CashSession.cash_register_id == register_id)
    
    if status:
        query = query.filter(CashSession.status == status)
    
    sessions = query.order_by(CashSession.opened_at.desc()).offset(skip).limit(limit).all()
    
    # Agregar información adicional
    result = []
    for session in sessions:
        session_dict = session.__dict__.copy()
        session_dict['user_name'] = session.user.full_name
        session_dict['cash_register_name'] = session.cash_register.name
        result.append(session_dict)
    
    return result


@router.post("/sessions", response_model=CashSessionResponse)
def open_cash_session(
    session_data: CashSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Abrir nueva sesión de caja"""
    # Verificar que la caja existe
    register = db.query(CashRegister).filter(
        CashRegister.id == session_data.cash_register_id
    ).first()
    
    if not register:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    
    # Verificar que no hay sesiones abiertas para esta caja
    open_session = db.query(CashSession).filter(
        and_(
            CashSession.cash_register_id == session_data.cash_register_id,
            CashSession.status == CASH_REGISTER_STATUS['OPEN']
        )
    ).first()
    
    if open_session:
        raise HTTPException(
            status_code=400, 
            detail="Ya existe una sesión abierta para esta caja"
        )
    
    # Generar número de sesión
    session_number = generate_session_number(db, session_data.cash_register_id)
    
    # Crear sesión
    db_session = CashSession(
        **session_data.dict(),
        user_id=current_user.id,
        session_number=session_number
    )
    db.add(db_session)
    db.flush()  # Esto genera el ID de la sesión
    
    # Crear movimiento de apertura
    opening_movement = CashMovement(
        session_id=db_session.id,
        movement_type=CASH_MOVEMENT_TYPE['OPENING'],
        amount=session_data.opening_amount,
        description="Apertura de caja",
        notes=session_data.opening_notes
    )
    db.add(opening_movement)
    
    db.commit()
    db.refresh(db_session)
    
    # Agregar información adicional
    session_dict = db_session.__dict__.copy()
    session_dict['user_name'] = db_session.user.full_name
    session_dict['cash_register_name'] = db_session.cash_register.name
    
    return session_dict


@router.post("/sessions/{session_id}/close", response_model=CashSessionResponse)
def close_cash_session(
    session_id: int,
    close_data: CashSessionClose,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cerrar sesión de caja"""
    session = db.query(CashSession).filter(CashSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    if session.status == CASH_REGISTER_STATUS['CLOSED']:
        raise HTTPException(
            status_code=400, 
            detail="La sesión ya está cerrada"
        )
    
    # Actualizar sesión
    session.closing_amount = close_data.closing_amount
    session.closing_notes = close_data.closing_notes
    session.closed_at = datetime.now()
    session.status = CASH_REGISTER_STATUS['CLOSED']
    
    # Crear movimiento de cierre
    closing_movement = CashMovement(
        session_id=session.id,
        movement_type=CASH_MOVEMENT_TYPE['CLOSING'],
        amount=close_data.closing_amount,
        description="Cierre de caja",
        notes=close_data.closing_notes
    )
    db.add(closing_movement)
    
    db.commit()
    db.refresh(session)
    
    # Agregar información adicional
    session_dict = session.__dict__.copy()
    session_dict['user_name'] = session.user.full_name
    session_dict['cash_register_name'] = session.cash_register.name
    
    return session_dict


@router.get("/sessions/{session_id}", response_model=CashSessionResponse)
def get_cash_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener sesión de caja por ID"""
    session = db.query(CashSession).filter(CashSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Agregar información adicional
    session_dict = session.__dict__.copy()
    session_dict['user_name'] = session.user.full_name
    session_dict['cash_register_name'] = session.cash_register.name
    
    return session_dict


# Endpoints para CashMovement
@router.get("/sessions/{session_id}/movements", response_model=List[CashMovementResponse])
def get_session_movements(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener movimientos de una sesión"""
    movements = db.query(CashMovement).filter(
        CashMovement.session_id == session_id
    ).order_by(CashMovement.created_at.desc()).all()
    
    return movements


@router.post("/movements", response_model=CashMovementResponse)
def create_movement(
    movement_data: CashMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nuevo movimiento de caja"""
    # Verificar que la sesión existe y está abierta
    session = db.query(CashSession).filter(CashSession.id == movement_data.session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    if session.status == CASH_REGISTER_STATUS['CLOSED']:
        raise HTTPException(
            status_code=400, 
            detail="No se pueden agregar movimientos a una sesión cerrada"
        )
    
    db_movement = CashMovement(**movement_data.dict())
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement


# Endpoints para reportes
@router.get("/sessions/{session_id}/summary", response_model=CashSessionSummary)
def get_session_summary(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener resumen de una sesión de caja"""
    session = db.query(CashSession).filter(CashSession.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Calcular totales por tipo de movimiento
    movements = db.query(
        CashMovement.movement_type,
        func.sum(CashMovement.amount).label('total')
    ).filter(CashMovement.session_id == session_id).group_by(CashMovement.movement_type).all()
    
    totals = {mov.movement_type: mov.total for mov in movements}
    
    # Calcular montos esperados
    total_sales = totals.get(CASH_MOVEMENT_TYPE['SALE'], Decimal('0'))
    total_refunds = totals.get(CASH_MOVEMENT_TYPE['REFUND'], Decimal('0'))
    total_expenses = totals.get(CASH_MOVEMENT_TYPE['EXPENSE'], Decimal('0'))
    total_withdrawals = totals.get(CASH_MOVEMENT_TYPE['WITHDRAWAL'], Decimal('0'))
    total_deposits = totals.get(CASH_MOVEMENT_TYPE['DEPOSIT'], Decimal('0'))
    
    expected_amount = (
        session.opening_amount + 
        total_sales + 
        total_deposits - 
        total_refunds - 
        total_expenses - 
        total_withdrawals
    )
    
    difference = None
    if session.closing_amount:
        difference = session.closing_amount - expected_amount
    
    return {
        "session_id": session.id,
        "session_number": session.session_number,
        "opened_at": session.opened_at,
        "closed_at": session.closed_at,
        "opening_amount": session.opening_amount,
        "closing_amount": session.closing_amount,
        "total_sales": total_sales,
        "total_refunds": total_refunds,
        "total_expenses": total_expenses,
        "total_withdrawals": total_withdrawals,
        "total_deposits": total_deposits,
        "expected_amount": expected_amount,
        "difference": difference,
        "status": session.status,
        "user_name": session.user.full_name,
        "cash_register_name": session.cash_register.name
    }


@router.get("/registers/{register_id}/report", response_model=CashRegisterReport)
def get_register_report(
    register_id: int,
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    end_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte de una caja registradora"""
    register = db.query(CashRegister).filter(CashRegister.id == register_id).first()
    
    if not register:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    
    # Obtener sesiones del período
    sessions = db.query(CashSession).filter(
        and_(
            CashSession.cash_register_id == register_id,
            func.date(CashSession.opened_at) >= start_date,
            func.date(CashSession.opened_at) <= end_date
        )
    ).all()
    
    # Calcular estadísticas
    total_sessions = len(sessions)
    open_sessions = len([s for s in sessions if s.status == CASH_REGISTER_STATUS['OPEN']])
    closed_sessions = total_sessions - open_sessions
    
    # Calcular totales de movimientos
    session_ids = [s.id for s in sessions]
    movements = db.query(
        CashMovement.movement_type,
        func.sum(CashMovement.amount).label('total')
    ).filter(
        CashMovement.session_id.in_(session_ids)
    ).group_by(CashMovement.movement_type).all()
    
    totals = {mov.movement_type: mov.total for mov in movements}
    
    total_amount = totals.get(CASH_MOVEMENT_TYPE['SALE'], Decimal('0'))
    total_sales = totals.get(CASH_MOVEMENT_TYPE['SALE'], Decimal('0'))
    total_expenses = totals.get(CASH_MOVEMENT_TYPE['EXPENSE'], Decimal('0'))
    
    return {
        "cash_register_id": register.id,
        "cash_register_name": register.name,
        "total_sessions": total_sessions,
        "open_sessions": open_sessions,
        "closed_sessions": closed_sessions,
        "total_amount": total_amount,
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "period_start": datetime.combine(start_date, datetime.min.time()),
        "period_end": datetime.combine(end_date, datetime.max.time())
    }
