"""
Módulo Unificado: Caja y Ventas
Integra el sistema de caja con ventas en un solo módulo
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.cash_register import CashRegister, CashSession, CashMovement, CashStatus, MovementType
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.auth.dependencies import get_current_active_user
from app.services.cash_service import CashService
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/caja-ventas", tags=["caja-ventas"])


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class AperturaCajaRequest(BaseModel):
    password: str
    fondo_inicial: Decimal
    notas_apertura: Optional[str] = None

class CierreCajaRequest(BaseModel):
    password: str
    monto_contado: Decimal
    notas_cierre: Optional[str] = None
    requiere_aprobacion: bool = True

class VentaRequest(BaseModel):
    items: List[Dict[str, Any]]  # [{"product_id": 1, "quantity": 2, "price": 1000}]
    customer_id: Optional[int] = None
    payment_method: str = "efectivo"
    notes: Optional[str] = None

class EgresoRequest(BaseModel):
    monto: Decimal
    concepto: str
    categoria: str = "gastos"
    notas: Optional[str] = None

class AprobacionCierreRequest(BaseModel):
    supervisor_password: str
    session_id: int
    aprobar: bool = True
    comentarios: Optional[str] = None


# ============================================================================
# ESTADO Y CONTROL DE CAJA
# ============================================================================

@router.get("/estado")
def get_estado_caja_ventas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estado completo de caja y ventas"""
    # Verificar que existe la caja principal
    cash_register = CashService.get_main_cash_register(db)
    if not cash_register:
        cash_register = CashService.create_main_cash_register(db)
    
    # Obtener sesión activa
    active_session = CashService.get_active_session(db, cash_register.id)
    today_session = CashService.get_today_session(db, cash_register.id)
    
    # Obtener información del negocio
    business_info = SettingsService.get_business_info(db)
    
    # Calcular estadísticas si hay sesión activa
    estadisticas = None
    if active_session:
        estadisticas = {
            "total_ventas": active_session.total_sales,
            "total_egresos": active_session.total_expenses,
            "monto_esperado": active_session.expected_amount,
            "fondo_inicial": active_session.opening_amount,
            "diferencia": active_session.expected_amount - active_session.opening_amount
        }
    
    return {
        "caja": {
            "id": cash_register.id,
            "name": cash_register.name,
            "register_number": cash_register.register_number
        },
        "business_info": business_info,
        "sesion_activa": active_session is not None,
        "sesion_hoy": today_session is not None,
        "puede_vender": active_session is not None,
        "requiere_caja": SettingsService.require_cash_register(db),
        "sesion_activa_info": {
            "id": active_session.id,
            "session_number": active_session.session_number,
            "opened_at": active_session.opened_at,
            "opening_amount": active_session.opening_amount,
            "opening_notes": active_session.opening_notes,
            "user_name": active_session.user.full_name,
            "estadisticas": estadisticas
        } if active_session else None,
        "sesion_hoy_info": {
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
# APERTURA DE CAJA
# ============================================================================

@router.post("/abrir-caja")
def abrir_caja(
    request: AperturaCajaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Abrir caja registradora con fondo inicial"""
    # Verificar contraseña
    if not SettingsService.verify_cash_register_password(db, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña de caja incorrecta"
        )
    
    try:
        # Obtener o crear caja principal
        cash_register = CashService.get_main_cash_register(db)
        if not cash_register:
            cash_register = CashService.create_main_cash_register(db)
        
        # Verificar que no hay sesión activa
        active_session = CashService.get_active_session(db, cash_register.id)
        if active_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya hay una sesión de caja activa"
            )
        
        # Abrir sesión
        session = CashService.open_session(
            db=db,
            cash_register_id=cash_register.id,
            user_id=current_user.id,
            opening_amount=request.fondo_inicial,
            opening_notes=request.notas_apertura
        )
        
        return {
            "message": "Caja abierta exitosamente",
            "sesion": {
                "id": session.id,
                "session_number": session.session_number,
                "opened_at": session.opened_at,
                "fondo_inicial": session.opening_amount,
                "user_name": session.user.full_name
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error abriendo caja: {str(e)}")


# ============================================================================
# REGISTRO DE VENTAS
# ============================================================================

@router.post("/registrar-venta")
def registrar_venta(
    request: VentaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Registrar una venta (solo si caja está abierta)"""
    # Verificar que hay sesión activa
    cash_register = CashService.get_main_cash_register(db)
    if not cash_register:
        raise HTTPException(status_code=404, detail="No hay caja registrada")
    
    active_session = CashService.get_active_session(db, cash_register.id)
    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede registrar venta. La caja debe estar abierta"
        )
    
    try:
        # Calcular total de la venta
        total_venta = Decimal('0')
        items_validos = []
        
        for item in request.items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            price = Decimal(str(item.get('price', 0)))
            
            # Verificar producto
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")
            
            subtotal = price * quantity
            total_venta += subtotal
            
            items_validos.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'subtotal': subtotal
            })
        
        if total_venta <= 0:
            raise HTTPException(status_code=400, detail="El total de la venta debe ser mayor a 0")
        
        # Crear la venta
        sale = Sale(
            user_id=current_user.id,
            customer_id=request.customer_id,
            total=total_venta,
            payment_method=request.payment_method,
            notes=request.notes,
            status="completada"
        )
        db.add(sale)
        db.flush()  # Para obtener el ID
        
        # Crear items de venta
        for item_data in items_validos:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['price'],
                subtotal=item_data['subtotal']
            )
            db.add(sale_item)
        
        # Registrar movimiento de caja
        CashService.register_sale_movement(
            db=db,
            session_id=active_session.id,
            sale_id=sale.id,
            amount=total_venta,
            description=f"Venta #{sale.id}"
        )
        
        db.commit()
        
        return {
            "message": "Venta registrada exitosamente",
            "venta": {
                "id": sale.id,
                "total": sale.total,
                "payment_method": sale.payment_method,
                "items_count": len(items_validos),
                "session_number": active_session.session_number
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error registrando venta: {str(e)}")


# ============================================================================
# REGISTRO DE EGRESOS
# ============================================================================

@router.post("/registrar-egreso")
def registrar_egreso(
    request: EgresoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Registrar un egreso (solo si caja está abierta)"""
    # Verificar que hay sesión activa
    cash_register = CashService.get_main_cash_register(db)
    if not cash_register:
        raise HTTPException(status_code=404, detail="No hay caja registrada")
    
    active_session = CashService.get_active_session(db, cash_register.id)
    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede registrar egreso. La caja debe estar abierta"
        )
    
    try:
        # Registrar movimiento de egreso
        movement = CashService.register_movement(
            db=db,
            session_id=active_session.id,
            movement_type=MovementType.EXPENSE,
            amount=request.monto,
            description=request.concepto,
            reference=f"Egreso - {request.categoria}",
            notes=request.notas
        )
        
        return {
            "message": "Egreso registrado exitosamente",
            "egreso": {
                "id": movement.id,
                "monto": movement.amount,
                "concepto": movement.description,
                "categoria": request.categoria,
                "session_number": active_session.session_number
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registrando egreso: {str(e)}")


# ============================================================================
# CIERRE DE CAJA
# ============================================================================

@router.post("/cerrar-caja")
def cerrar_caja(
    request: CierreCajaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cerrar caja registradora con declaración de monto contado"""
    # Verificar contraseña
    if not SettingsService.verify_cash_register_password(db, request.password):
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
        
        # Si requiere aprobación, marcar como pendiente
        if request.requiere_aprobacion:
            # Aquí podrías implementar lógica de aprobación
            # Por ahora, cerramos directamente
            pass
        
        # Cerrar sesión
        session = CashService.close_session(
            db=db,
            session_id=active_session.id,
            closing_amount=request.monto_contado,
            closing_notes=request.notas_cierre
        )
        
        # Obtener resumen final
        summary = CashService.get_session_summary(db, session.id)
        
        return {
            "message": "Caja cerrada exitosamente",
            "sesion": {
                "id": session.id,
                "session_number": session.session_number,
                "closed_at": session.closed_at,
                "monto_contado": session.closing_amount,
                "user_name": session.user.full_name
            },
            "resumen": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cerrando caja: {str(e)}")


# ============================================================================
# REPORTES Y MOVIMIENTOS
# ============================================================================

@router.get("/movimientos")
def get_movimientos_sesion(
    session_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener movimientos de la sesión actual"""
    # Si no se especifica sesión, usar la activa
    if not session_id:
        cash_register = CashService.get_main_cash_register(db)
        if cash_register:
            active_session = CashService.get_active_session(db, cash_register.id)
            if active_session:
                session_id = active_session.id
    
    if not session_id:
        return []
    
    movements = db.query(CashMovement).filter(
        CashMovement.session_id == session_id
    ).order_by(CashMovement.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for movement in movements:
        movement_data = {
            "id": movement.id,
            "tipo": movement.movement_type,
            "monto": movement.amount,
            "descripcion": movement.description,
            "referencia": movement.reference,
            "notas": movement.notes,
            "fecha": movement.created_at,
            "session_number": movement.session.session_number
        }
        result.append(movement_data)
    
    return result


@router.get("/reporte-sesion/{session_id}")
def get_reporte_sesion(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte completo de una sesión"""
    summary = CashService.get_session_summary(db, session_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    return summary


@router.get("/reporte-diario")
def get_reporte_diario(
    fecha: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte diario de caja y ventas"""
    return CashService.get_daily_report(db, fecha)
