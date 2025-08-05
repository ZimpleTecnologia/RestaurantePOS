"""
Router de ventas
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.sale import Sale, SaleItem, PaymentMethod, SaleStatus
from app.models.product import Product
from app.auth.dependencies import get_current_active_user
from app.schemas.sale import (
    SaleCreate, SaleUpdate, SaleResponse, SaleWithDetails,
    SaleItemCreate, SaleItemResponse,
    PaymentMethodCreate, PaymentMethodResponse
)

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


@router.get("/", response_model=List[SaleWithDetails])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    status: Optional[SaleStatus] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de ventas"""
    query = db.query(Sale)
    
    if status:
        query = query.filter(Sale.status == status)
    
    if start_date:
        query = query.filter(func.date(Sale.created_at) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Sale.created_at) <= end_date)
    
    if user_id:
        query = query.filter(Sale.user_id == user_id)
    
    sales = query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
    return sales


@router.post("/", response_model=SaleResponse)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nueva venta"""
    # Generar número de venta
    sale_number = generate_sale_number(db)
    
    # Crear venta
    db_sale = Sale(
        sale_number=sale_number,
        user_id=current_user.id,
        **sale_data.dict(exclude={'items', 'payments'})
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
        item_total = (item_data.unit_price * item_data.quantity) - item_data.discount
        
        db_item = SaleItem(
            sale_id=db_sale.id,
            **item_data.dict(),
            total=item_total
        )
        db.add(db_item)
        
        # Actualizar stock
        product.stock -= item_data.quantity
    
    # Crear métodos de pago
    for payment_data in sale_data.payments:
        db_payment = PaymentMethod(
            sale_id=db_sale.id,
            **payment_data.dict()
        )
        db.add(db_payment)
    
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
    return sale


@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    sale_data: SaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar venta"""
    db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # Solo permitir actualizar ventas pendientes
    if db_sale.status != SaleStatus.PENDIENTE:
        raise HTTPException(
            status_code=400, 
            detail="Solo se pueden actualizar ventas pendientes"
        )
    
    for field, value in sale_data.dict(exclude_unset=True).items():
        setattr(db_sale, field, value)
    
    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.post("/{sale_id}/complete")
def complete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Completar venta"""
    db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    if db_sale.status != SaleStatus.PENDIENTE:
        raise HTTPException(
            status_code=400, 
            detail="Solo se pueden completar ventas pendientes"
        )
    
    db_sale.status = SaleStatus.COMPLETADA
    db_sale.completed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Venta completada exitosamente"}


@router.post("/{sale_id}/cancel")
def cancel_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancelar venta y devolver stock"""
    db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    if db_sale.status not in [SaleStatus.PENDIENTE, SaleStatus.COMPLETADA]:
        raise HTTPException(
            status_code=400, 
            detail="No se puede cancelar esta venta"
        )
    
    # Devolver stock si la venta estaba completada
    if db_sale.status == SaleStatus.COMPLETADA:
        for item in db_sale.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity
    
    db_sale.status = SaleStatus.CANCELADA
    db.commit()
    
    return {"message": "Venta cancelada exitosamente"}


@router.get("/reports/daily")
def get_daily_report(
    report_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte diario de ventas"""
    # Ventas del día
    sales = db.query(Sale).filter(
        func.date(Sale.created_at) == report_date,
        Sale.status == SaleStatus.COMPLETADA
    ).all()
    
    total_sales = len(sales)
    total_amount = sum(sale.total for sale in sales)
    total_tips = sum(sale.tip for sale in sales)
    total_commission = sum(sale.commission for sale in sales)
    
    # Métodos de pago
    payment_methods = {}
    for sale in sales:
        for payment in sale.payments:
            method = payment.payment_type.value
            if method not in payment_methods:
                payment_methods[method] = 0
            payment_methods[method] += payment.amount
    
    return {
        "date": report_date,
        "total_sales": total_sales,
        "total_amount": total_amount,
        "total_tips": total_tips,
        "total_commission": total_commission,
        "payment_methods": payment_methods
    } 