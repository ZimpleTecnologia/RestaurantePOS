"""
Router de ventas - Integrado con Sistema de Caja Protegido
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import get_db
from app.models.user import User
from app.models.sale import Sale, SaleItem, SaleStatus
from app.models.product import Product
from app.models.customer import Customer
from app.auth.dependencies import get_current_active_user
from app.schemas.sale import (
    SaleCreate, SaleUpdate, SaleResponse, SaleWithDetails,
    SaleItemCreate, SaleItemResponse
)
from app.services.cash_service import CashService
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/sales", tags=["ventas"])


def generate_sale_number(db: Session) -> str:
    """Generar número único de venta"""
    today = date.today()
    prefix = f"V{today.strftime('%Y%m%d')}"
    
    # Contar ventas del día
    count = db.query(func.count(Sale.id)).filter(
        func.date(Sale.created_at) == today
    ).scalar()
    
    return f"{prefix}-{count + 1:04d}"


def check_cash_register_status(db: Session) -> dict:
    """Verificar estado de la caja antes de crear ventas"""
    # Verificar si se requiere caja abierta para ventas
    require_cash_register = SettingsService.require_cash_register(db)
    
    if not require_cash_register:
        return {
            "cash_register": None,
            "active_session": None,
            "can_create_sale": True,
            "require_cash_register": False
        }
    
    cash_register = CashService.get_main_cash_register(db)
    if not cash_register:
        # Crear caja principal si no existe
        cash_register = CashService.create_main_cash_register(db)
    
    active_session = CashService.get_active_session(db, cash_register.id)
    
    return {
        "cash_register": cash_register,
        "active_session": active_session,
        "can_create_sale": active_session is not None,
        "require_cash_register": True
    }


@router.get("/", response_model=List[SaleWithDetails])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de ventas"""
    sales = db.query(Sale).order_by(Sale.id.desc()).offset(skip).limit(limit).all()
    
    # Agregar información del cliente
    result = []
    for sale in sales:
        sale_dict = {
            "id": sale.id,
            "sale_number": sale.sale_number,
            "customer_id": sale.customer_id,
            "user_id": sale.user_id,
            "total": sale.total,
            "status": sale.status,
            "items": [],
            "customer_name": None
        }
        
        # Obtener nombre del cliente
        if sale.customer_id:
            customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
            if customer:
                sale_dict["customer_name"] = customer.full_name
        
        # Obtener items de la venta
        items = db.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
        sale_dict["items"] = [
            {
                "id": item.id,
                "sale_id": item.sale_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total": item.total
            }
            for item in items
        ]
        
        result.append(sale_dict)
    
    return result


@router.get("/cash-status")
def get_cash_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estado actual de la caja para ventas"""
    cash_status = check_cash_register_status(db)
    
    return {
        "cash_register_id": cash_status["cash_register"].id if cash_status["cash_register"] else None,
        "cash_register_name": cash_status["cash_register"].name if cash_status["cash_register"] else None,
        "has_active_session": cash_status["active_session"] is not None,
        "can_create_sale": cash_status["can_create_sale"],
        "require_cash_register": cash_status["require_cash_register"],
        "active_session": {
            "id": cash_status["active_session"].id,
            "session_number": cash_status["active_session"].session_number,
            "opened_at": cash_status["active_session"].opened_at,
            "opening_amount": cash_status["active_session"].opening_amount,
            "user_name": cash_status["active_session"].user.full_name
        } if cash_status["active_session"] else None
    }


@router.post("/", response_model=SaleResponse)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nueva venta - Solo si la caja está abierta (si se requiere)"""
    
    # Verificar estado de la caja
    cash_status = check_cash_register_status(db)
    
    if not cash_status["can_create_sale"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede crear una venta. La caja debe estar abierta. Abra una sesión de caja primero."
        )
    
    # Generar número de venta
    sale_number = generate_sale_number(db)
    
    # Crear venta
    db_sale = Sale(
        sale_number=sale_number,
        user_id=current_user.id,
        customer_id=sale_data.customer_id,
        total=sale_data.total,
        status="completada"
    )
    
    db.add(db_sale)
    db.flush()  # Para obtener el ID de la venta
    
    # Crear items de venta
    for item_data in sale_data.items:
        # Verificar stock
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item_data.product_id} no encontrado")
        
        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente para {product.name}. Disponible: {product.stock}"
            )
        
        # Calcular total del item
        item_total = item_data.price * item_data.quantity
        
        db_item = SaleItem(
            sale_id=db_sale.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.price,
            total=item_total
        )
        db.add(db_item)
        
        # Actualizar stock
        product.stock -= item_data.quantity
    
    # Registrar movimiento en caja (solo si hay caja activa)
    if cash_status["active_session"]:
        try:
            CashService.register_sale_movement(
                db=db,
                session_id=cash_status["active_session"].id,
                sale_id=db_sale.id,
                amount=sale_data.total,
                description=f"Venta {sale_number}"
            )
        except Exception as e:
            # Si falla el registro en caja, hacer rollback de la venta
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error registrando venta en caja: {str(e)}"
            )
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/{sale_id}", response_model=SaleWithDetails)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener venta por ID"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # Agregar información del cliente
    sale_dict = {
        "id": sale.id,
        "sale_number": sale.sale_number,
        "customer_id": sale.customer_id,
        "user_id": sale.user_id,
        "total": sale.total,
        "status": sale.status,
        "items": [],
        "customer_name": None
    }
    
    # Obtener nombre del cliente
    if sale.customer_id:
        customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
        if customer:
            sale_dict["customer_name"] = customer.full_name
    
    # Obtener items de la venta
    items = db.query(SaleItem).filter(SaleItem.sale_id == sale.id).all()
    sale_dict["items"] = [
        {
            "id": item.id,
            "sale_id": item.sale_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total": item.total
        }
        for item in items
    ]
    
    return sale_dict


@router.get("/reports/daily")
def get_daily_report(
    report_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reporte diario de ventas"""
    # Ventas del día
    sales = db.query(Sale).filter(
        func.date(Sale.created_at) == report_date,
        Sale.status == "completada"
    ).all()
    
    total_sales = len(sales)
    total_amount = sum(sale.total for sale in sales)
    
    # Obtener reporte de caja del día (solo si se requiere caja)
    cash_report = None
    if SettingsService.require_cash_register(db):
        cash_report = CashService.get_daily_report(db, report_date)
    
    return {
        "date": report_date,
        "total_sales": total_sales,
        "total_amount": total_amount,
        "cash_report": cash_report,
        "require_cash_register": SettingsService.require_cash_register(db)
    }


@router.get("/reports/weekly")
def get_weekly_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reporte semanal de ventas"""
    from datetime import timedelta
    
    # Obtener fecha de hace 7 días
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    
    # Ventas de la semana
    sales = db.query(Sale).filter(
        func.date(Sale.created_at) >= start_date,
        func.date(Sale.created_at) <= end_date,
        Sale.status == "completada"
    ).all()
    
    # Agrupar por día
    daily_sales = {}
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        daily_sales[current_date.strftime('%Y-%m-%d')] = 0
    
    for sale in sales:
        sale_date = sale.created_at.date().strftime('%Y-%m-%d')
        if sale_date in daily_sales:
            daily_sales[sale_date] += sale.total
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_sales": len(sales),
        "total_amount": sum(sale.total for sale in sales),
        "daily_sales": list(daily_sales.values()),
        "labels": [d.strftime('%a') for d in [start_date + timedelta(days=i) for i in range(7)]]
    }