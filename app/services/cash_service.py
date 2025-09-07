"""
Servicio para el manejo de caja - Centralizado y Profesional
"""
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.cash_register import CashRegister, CashSession, CashMovement, CashStatus, MovementType
from app.models.user import User
from app.models.sale import Sale


class CashService:
    """Servicio para manejo de caja"""
    
    @staticmethod
    def get_main_cash_register(db: Session) -> Optional[CashRegister]:
        """Obtener la caja principal (solo una caja por ubicación)"""
        return db.query(CashRegister).filter(CashRegister.is_active == True).first()
    
    @staticmethod
    def create_main_cash_register(db: Session, name: str = "Caja Principal") -> CashRegister:
        """Crear la caja principal si no existe"""
        cash_register = CashService.get_main_cash_register(db)
        if not cash_register:
            # Generar número de registro único
            register_number = "CAJA001"
            
            cash_register = CashRegister(
                register_number=register_number,
                name=name
            )
            db.add(cash_register)
            db.commit()
            db.refresh(cash_register)
        return cash_register
    
    @staticmethod
    def get_active_session(db: Session, cash_register_id: int) -> Optional[CashSession]:
        """Obtener la sesión activa de caja"""
        return db.query(CashSession).filter(
            and_(
                CashSession.cash_register_id == cash_register_id,
                CashSession.status == CashStatus.OPEN
            )
        ).first()
    
    @staticmethod
    def get_today_session(db: Session, cash_register_id: int) -> Optional[CashSession]:
        """Obtener la última sesión del día actual"""
        today = date.today()
        return db.query(CashSession).filter(
            and_(
                CashSession.cash_register_id == cash_register_id,
                func.date(CashSession.opened_at) == today
            )
        ).order_by(CashSession.opened_at.desc()).first()
    
    @staticmethod
    def can_create_sale(db: Session, cash_register_id: int) -> bool:
        """Verificar si se puede crear una venta (caja debe estar abierta)"""
        active_session = CashService.get_active_session(db, cash_register_id)
        return active_session is not None
    
    @staticmethod
    def open_session(
        db: Session, 
        cash_register_id: int, 
        user_id: int, 
        opening_amount: Decimal = Decimal('0'),
        opening_notes: str = None
    ) -> CashSession:
        """Abrir una nueva sesión de caja"""
        
        # Verificar que no hay sesión activa
        active_session = CashService.get_active_session(db, cash_register_id)
        if active_session:
            raise ValueError("Ya existe una sesión abierta para esta caja")
        
        # Generar número de sesión único
        today = date.today()
        # Contar sesiones del día para generar número único
        session_count = db.query(CashSession).filter(
            and_(
                CashSession.cash_register_id == cash_register_id,
                func.date(CashSession.opened_at) == today
            )
        ).count()
        
        session_number = f"S{today.strftime('%Y%m%d')}-{cash_register_id:02d}-{session_count + 1:02d}"
        
        # Crear sesión
        session = CashSession(
            cash_register_id=cash_register_id,
            user_id=user_id,
            session_number=session_number,
            opening_amount=opening_amount,
            opening_notes=opening_notes
        )
        db.add(session)
        db.flush()  # Para obtener el ID
        
        # Crear movimiento de apertura
        opening_movement = CashMovement(
            session_id=session.id,
            movement_type=MovementType.OPENING,
            amount=opening_amount,
            description="Apertura de caja",
            notes=opening_notes
        )
        db.add(opening_movement)
        
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def close_session(
        db: Session, 
        session_id: int, 
        closing_amount: Decimal,
        closing_notes: str = None
    ) -> CashSession:
        """Cerrar una sesión de caja"""
        
        session = db.query(CashSession).filter(CashSession.id == session_id).first()
        if not session:
            raise ValueError("Sesión no encontrada")
        
        if session.status == CashStatus.CLOSED:
            raise ValueError("La sesión ya está cerrada")
        
        # Actualizar sesión
        session.closing_amount = closing_amount
        session.closing_notes = closing_notes
        session.closed_at = datetime.now()
        session.status = CashStatus.CLOSED
        
        # Crear movimiento de cierre
        closing_movement = CashMovement(
            session_id=session.id,
            movement_type=MovementType.CLOSING,
            amount=closing_amount,
            description="Cierre de caja",
            notes=closing_notes
        )
        db.add(closing_movement)
        
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def register_sale_movement(
        db: Session, 
        session_id: int, 
        sale_id: int, 
        amount: Decimal,
        description: str = None
    ) -> CashMovement:
        """Registrar movimiento de venta en caja"""
        
        if not description:
            description = f"Venta #{sale_id}"
        
        movement = CashMovement(
            session_id=session_id,
            movement_type=MovementType.SALE,
            amount=amount,
            description=description,
            reference=str(sale_id)
        )
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement
    
    @staticmethod
    def register_movement(
        db: Session,
        session_id: int,
        movement_type: MovementType,
        amount: Decimal,
        description: str,
        reference: str = None,
        notes: str = None
    ) -> CashMovement:
        """Registrar movimiento genérico en caja"""
        
        movement = CashMovement(
            session_id=session_id,
            movement_type=movement_type,
            amount=amount,
            description=description,
            reference=reference,
            notes=notes
        )
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement
    
    @staticmethod
    def get_session_summary(db: Session, session_id: int) -> dict:
        """Obtener resumen de una sesión de caja"""
        session = db.query(CashSession).filter(CashSession.id == session_id).first()
        if not session:
            return None
        
        # Calcular totales
        total_sales = sum(
            m.amount for m in session.movements 
            if m.movement_type == MovementType.SALE
        )
        total_expenses = sum(
            m.amount for m in session.movements 
            if m.movement_type == MovementType.EXPENSE
        )
        total_refunds = sum(
            m.amount for m in session.movements 
            if m.movement_type == MovementType.REFUND
        )
        
        expected_amount = session.opening_amount + total_sales - total_expenses - total_refunds
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
            "total_expenses": total_expenses,
            "total_refunds": total_refunds,
            "expected_amount": expected_amount,
            "difference": difference,
            "status": session.status,
            "user_name": session.user.full_name,
            "cash_register_name": session.cash_register.name
        }
    
    @staticmethod
    def get_daily_report(db: Session, report_date: date = None) -> dict:
        """Obtener reporte diario de caja"""
        if not report_date:
            report_date = date.today()
        
        # Obtener sesión del día
        session = db.query(CashSession).filter(
            func.date(CashSession.opened_at) == report_date
        ).first()
        
        if not session:
            return {
                "date": report_date,
                "has_session": False,
                "message": "No hay sesión de caja para este día"
            }
        
        summary = CashService.get_session_summary(db, session.id)
        summary["date"] = report_date
        summary["has_session"] = True
        
        return summary
