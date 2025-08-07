"""
Router de clientes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.customer import Customer, Credit, Payment
from app.auth.dependencies import get_current_active_user, require_admin
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CreditCreate, CreditResponse, PaymentCreate, PaymentResponse
)

router = APIRouter(prefix="/customers", tags=["clientes"])


@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de clientes"""
    query = db.query(Customer).filter(Customer.is_active == True)
    
    if search:
        query = query.filter(
            (Customer.first_name.ilike(f"%{search}%")) |
            (Customer.last_name.ilike(f"%{search}%")) |
            (Customer.document_number.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )
    
    customers = query.offset(skip).limit(limit).all()
    return customers


@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nuevo cliente"""
    # Verificar si el documento ya existe
    existing_customer = db.query(Customer).filter(
        Customer.document_number == customer_data.document_number
    ).first()
    
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un cliente con este documento"
        )
    
    db_customer = Customer(**customer_data.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener cliente por ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar cliente"""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    for field, value in customer_data.dict(exclude_unset=True).items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Eliminar cliente (desactivar)"""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db_customer.is_active = False
    db.commit()
    return {"message": "Cliente eliminado exitosamente"}


# Rutas para créditos
@router.get("/{customer_id}/credits", response_model=List[CreditResponse])
def get_customer_credits(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener créditos de un cliente"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    credits = db.query(Credit).filter(
        Credit.customer_id == customer_id,
        Credit.is_active == True
    ).all()
    return credits


@router.post("/{customer_id}/credits", response_model=CreditResponse)
def create_customer_credit(
    customer_id: int,
    credit_data: CreditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear crédito para un cliente"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Verificar límite de crédito
    if customer.current_balance + credit_data.amount > customer.credit_limit:
        raise HTTPException(
            status_code=400,
            detail="El monto excede el límite de crédito del cliente"
        )
    
    db_credit = Credit(
        customer_id=customer_id,
        **credit_data.dict()
    )
    db.add(db_credit)
    
    # Actualizar balance del cliente
    customer.current_balance += credit_data.amount
    
    db.commit()
    db.refresh(db_credit)
    return db_credit


# Rutas para pagos
@router.get("/{customer_id}/payments", response_model=List[PaymentResponse])
def get_customer_payments(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener pagos de un cliente"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    payments = db.query(Payment).filter(Payment.customer_id == customer_id).all()
    return payments


@router.post("/{customer_id}/payments", response_model=PaymentResponse)
def create_customer_payment(
    customer_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear pago para un cliente"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db_payment = Payment(
        customer_id=customer_id,
        **payment_data.dict()
    )
    db.add(db_payment)
    
    # Actualizar balance del cliente
    customer.current_balance -= payment_data.amount
    
    # Si el pago está asociado a un crédito específico, actualizar el balance del crédito
    if payment_data.credit_id:
        credit = db.query(Credit).filter(Credit.id == payment_data.credit_id).first()
        if credit:
            credit.balance -= payment_data.amount
            if credit.balance <= 0:
                credit.is_active = False
    
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.get("/reports/debts")
def get_debts_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte de deudas de clientes"""
    from sqlalchemy import func
    
    # Clientes con deudas
    customers_with_debts = db.query(Customer).filter(
        Customer.current_balance > 0,
        Customer.is_active == True
    ).all()
    
    total_debt = sum(customer.current_balance for customer in customers_with_debts)
    
    return {
        "total_customers_with_debts": len(customers_with_debts),
        "total_debt_amount": total_debt,
        "customers_with_debts": [
            {
                "id": customer.id,
                "full_name": customer.full_name,
                "current_balance": customer.current_balance,
                "credit_limit": customer.credit_limit
            }
            for customer in customers_with_debts[:10]  # Top 10
        ]
    }


@router.get("/reports/customers")
def get_customers_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte general de clientes"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Estadísticas generales
    total_customers = db.query(Customer).filter(Customer.is_active == True).count()
    new_customers_this_month = db.query(Customer).filter(
        Customer.created_at >= datetime.now().replace(day=1),
        Customer.is_active == True
    ).count()
    
    # Clientes por ciudad
    customers_by_city = db.query(
        Customer.city,
        func.count(Customer.id).label('total_customers')
    ).filter(Customer.is_active == True)\
     .group_by(Customer.city)\
     .order_by(func.count(Customer.id).desc())\
     .limit(10).all()
    
    # Top clientes por compras (si hay ventas)
    from app.models.sale import Sale, SaleStatus
    
    top_customers = db.query(
        Customer.full_name,
        func.count(Sale.id).label('total_sales'),
        func.sum(Sale.total).label('total_amount')
    ).join(Sale, Customer.id == Sale.customer_id)\
     .filter(
        Sale.status == SaleStatus.COMPLETADA,
        Customer.is_active == True
    ).group_by(Customer.id, Customer.full_name)\
     .order_by(func.sum(Sale.total).desc())\
     .limit(10).all()
    
    return {
        "total_customers": total_customers,
        "new_customers_this_month": new_customers_this_month,
        "customers_by_city": [
            {
                "city": item.city or "Sin ciudad",
                "total_customers": item.total_customers
            }
            for item in customers_by_city
        ],
        "top_customers": [
            {
                "name": item.full_name,
                "total_sales": item.total_sales,
                "total_amount": float(item.total_amount or 0)
            }
            for item in top_customers
        ]
    }
    """Obtener reporte de deudas por cliente"""
    customers_with_debts = db.query(Customer).filter(
        Customer.current_balance > 0,
        Customer.is_active == True
    ).all()
    
    total_debt = sum(customer.current_balance for customer in customers_with_debts)
    
    return {
        "total_debt": total_debt,
        "customers_with_debts": len(customers_with_debts),
        "customers": [
            {
                "id": customer.id,
                "name": customer.full_name,
                "document": customer.document_number,
                "balance": customer.current_balance,
                "credit_limit": customer.credit_limit
            }
            for customer in customers_with_debts
        ]
    } 