"""
Router de ventas
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
from app.models.cash_register import CashSession, CashMovement, CASH_REGISTER_STATUS, CASH_MOVEMENT_TYPE
from app.auth.dependencies import get_current_active_user
from app.schemas.sale import (
    SaleCreate, SaleUpdate, SaleResponse, SaleWithDetails,
    SaleItemCreate, SaleItemResponse
)

router = APIRouter(prefix="/sales", tags=["ventas"])


def get_active_cash_session(db: Session, user_id: int) -> Optional[CashSession]:
    """Obtener la sesión activa de caja para el usuario"""
    active_session = db.query(CashSession).filter(
        and_(
            CashSession.user_id == user_id,
            CashSession.status == CASH_REGISTER_STATUS['OPEN']
        )
    ).first()
    return active_session


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de ventas"""
    sales = db.query(Sale).order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
    
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
            "created_at": sale.created_at,
            "completed_at": sale.completed_at,
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
        customer_id=sale_data.customer_id,
        total=sale_data.total,
        status=SaleStatus.COMPLETADA
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
    
    # Crear movimiento de caja automáticamente
    active_session = get_active_cash_session(db, current_user.id)
    if active_session:
        cash_movement = CashMovement(
            session_id=active_session.id,
            movement_type=CASH_MOVEMENT_TYPE['SALE'],
            amount=sale_data.total,
            description=f"Venta {sale_number}",
            reference=str(db_sale.id),
            notes=f"Venta automática generada por el sistema"
        )
        db.add(cash_movement)
    else:
        # Si no hay sesión activa, podemos lanzar un error o continuar según la política
        # Por ahora continuamos sin crear el movimiento pero registramos la venta
        # En un entorno de producción, podrías querer lanzar un error aquí
        pass
    
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
        "created_at": sale.created_at,
        "completed_at": sale.completed_at,
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
    """Obtener reporte diario de ventas"""
    # Ventas del día
    sales = db.query(Sale).filter(
        func.date(Sale.created_at) == report_date,
        Sale.status == SaleStatus.COMPLETADA
    ).all()
    
    total_sales = len(sales)
    total_amount = sum(sale.total for sale in sales)
    
    return {
        "date": report_date,
        "total_sales": total_sales,
        "total_amount": total_amount
    }


@router.get("/reports/weekly")
def get_weekly_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte semanal de ventas"""
    from datetime import timedelta
    
    # Obtener fecha de hace 7 días
    end_date = date.today()
    start_date = end_date - timedelta(days=6)
    
    # Ventas de la semana
    sales = db.query(Sale).filter(
        func.date(Sale.created_at) >= start_date,
        func.date(Sale.created_at) <= end_date,
        Sale.status == SaleStatus.COMPLETADA
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


@router.get("/reports/monthly")
def get_monthly_report(
    year: int = Query(default_factory=lambda: date.today().year),
    month: int = Query(default_factory=lambda: date.today().month),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte mensual de ventas"""
    from datetime import datetime
    
    # Ventas del mes
    sales = db.query(Sale).filter(
        func.extract('year', Sale.created_at) == year,
        func.extract('month', Sale.created_at) == month,
        Sale.status == SaleStatus.COMPLETADA
    ).all()
    
    total_sales = len(sales)
    total_amount = sum(sale.total for sale in sales)
    
    # Top productos vendidos
    product_sales = db.query(
        Product.name,
        func.sum(SaleItem.quantity).label('total_quantity'),
        func.sum(SaleItem.total).label('total_amount')
    ).join(SaleItem, Product.id == SaleItem.product_id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(
        func.extract('year', Sale.created_at) == year,
        func.extract('month', Sale.created_at) == month,
        Sale.status == SaleStatus.COMPLETADA
    ).group_by(Product.name)\
     .order_by(func.sum(SaleItem.quantity).desc())\
     .limit(10).all()
    
    return {
        "year": year,
        "month": month,
        "total_sales": total_sales,
        "total_amount": total_amount,
        "top_products": [
            {
                "name": item.name,
                "quantity": item.total_quantity,
                "amount": float(item.total_amount)
            }
            for item in product_sales
        ]
    }


@router.get("/without-cash-movement")
def get_sales_without_cash_movement(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener ventas que no tienen movimiento de caja asociado"""
    # Obtener todas las ventas completadas
    sales = db.query(Sale).filter(
        Sale.status == SaleStatus.COMPLETADA
    ).all()
    
    # Obtener todos los movimientos de caja que son ventas
    cash_movements = db.query(CashMovement).filter(
        CashMovement.movement_type == CASH_MOVEMENT_TYPE['SALE']
    ).all()
    
    # Crear un set de IDs de ventas que ya tienen movimiento de caja
    sales_with_movement = set()
    for movement in cash_movements:
        try:
            sale_id = int(movement.reference)
            sales_with_movement.add(sale_id)
        except (ValueError, TypeError):
            continue
    
    # Filtrar ventas sin movimiento de caja
    sales_without_movement = []
    for sale in sales:
        if sale.id not in sales_with_movement:
            sales_without_movement.append({
                "id": sale.id,
                "sale_number": sale.sale_number,
                "total": sale.total,
                "created_at": sale.created_at,
                "user_name": sale.user.full_name
            })
    
    return {
        "sales_without_movement": sales_without_movement,
        "count": len(sales_without_movement)
    }


@router.post("/{sale_id}/create-cash-movement")
def create_cash_movement_for_sale(
    sale_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear movimiento de caja para una venta específica"""
    # Verificar que la venta existe
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # Verificar que la venta está completada
    if sale.status != SaleStatus.COMPLETADA:
        raise HTTPException(status_code=400, detail="Solo se pueden crear movimientos para ventas completadas")
    
    # Verificar que la sesión existe y está abierta
    session = db.query(CashSession).filter(CashSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión de caja no encontrada")
    
    if session.status != CASH_REGISTER_STATUS['OPEN']:
        raise HTTPException(status_code=400, detail="Solo se pueden agregar movimientos a sesiones abiertas")
    
    # Verificar que no existe ya un movimiento para esta venta
    existing_movement = db.query(CashMovement).filter(
        and_(
            CashMovement.movement_type == CASH_MOVEMENT_TYPE['SALE'],
            CashMovement.reference == str(sale_id)
        )
    ).first()
    
    if existing_movement:
        raise HTTPException(status_code=400, detail="Ya existe un movimiento de caja para esta venta")
    
    # Crear el movimiento de caja
    cash_movement = CashMovement(
        session_id=session_id,
        movement_type=CASH_MOVEMENT_TYPE['SALE'],
        amount=sale.total,
        description=f"Venta {sale.sale_number}",
        reference=str(sale_id),
        notes=f"Movimiento creado manualmente para venta {sale.sale_number}"
    )
    
    db.add(cash_movement)
    db.commit()
    db.refresh(cash_movement)
    
    return {
        "message": "Movimiento de caja creado exitosamente",
        "movement_id": cash_movement.id,
        "sale_id": sale_id,
        "amount": cash_movement.amount
    }


@router.get("/cash-integration/summary")
def get_cash_integration_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener resumen de la integración entre ventas y caja"""
    # Total de ventas completadas
    total_sales = db.query(func.count(Sale.id)).filter(
        Sale.status == SaleStatus.COMPLETADA
    ).scalar()
    
    total_sales_amount = db.query(func.sum(Sale.total)).filter(
        Sale.status == SaleStatus.COMPLETADA
    ).scalar() or 0
    
    # Total de movimientos de caja por ventas
    total_cash_movements = db.query(func.count(CashMovement.id)).filter(
        CashMovement.movement_type == CASH_MOVEMENT_TYPE['SALE']
    ).scalar()
    
    total_cash_amount = db.query(func.sum(CashMovement.amount)).filter(
        CashMovement.movement_type == CASH_MOVEMENT_TYPE['SALE']
    ).scalar() or 0
    
    # Ventas sin movimiento de caja
    sales_without_movement = db.query(func.count(Sale.id)).filter(
        Sale.status == SaleStatus.COMPLETADA
    ).scalar()
    
    # Restar las que sí tienen movimiento
    sales_with_movement = db.query(func.count(CashMovement.id)).filter(
        CashMovement.movement_type == CASH_MOVEMENT_TYPE['SALE']
    ).scalar()
    
    sales_without_movement = sales_without_movement - sales_with_movement
    
    return {
        "total_sales": total_sales,
        "total_sales_amount": float(total_sales_amount),
        "total_cash_movements": total_cash_movements,
        "total_cash_amount": float(total_cash_amount),
        "sales_without_movement": max(0, sales_without_movement),
        "integration_percentage": round((total_cash_movements / total_sales * 100) if total_sales > 0 else 0, 2)
    }


@router.get("/{sale_id}/print")
def print_sale_ticket(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generar ticket de venta para imprimir"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # Obtener información del cliente
    customer_name = "Cliente General"
    if sale.customer_id:
        customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
        if customer:
            customer_name = customer.full_name
    
    # Obtener items de la venta con información del producto
    items = db.query(SaleItem, Product.name, Product.code).join(
        Product, SaleItem.product_id == Product.id
    ).filter(SaleItem.sale_id == sale.id).all()
    
    # Generar HTML del ticket
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Ticket de Venta</title>
        <style>
        /* Estilos para tickets de impresión */
        @media print {{
            body {{
                font-family: 'Courier New', monospace !important;
                font-size: 12px !important;
                margin: 0 !important;
                padding: 10px !important;
                width: 300px !important;
                background: white !important;
                color: black !important;
            }}
            
            .ticket-header {{
                text-align: center;
                border-bottom: 1px dashed #000;
                padding-bottom: 10px;
                margin-bottom: 10px;
            }}
            
            .ticket-title {{
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            .ticket-subtitle {{
                font-size: 10px;
                color: #666;
            }}
            
            .ticket-info {{
                margin-bottom: 10px;
            }}
            
            .ticket-items {{
                border-bottom: 1px dashed #000;
                padding-bottom: 10px;
                margin-bottom: 10px;
            }}
            
            .ticket-item {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 3px;
            }}
            
            .ticket-item-name {{
                flex: 1;
            }}
            
            .ticket-item-qty {{
                text-align: center;
                margin: 0 5px;
            }}
            
            .ticket-item-price {{
                text-align: right;
                margin-left: 5px;
            }}
            
            .ticket-totals {{
                text-align: right;
            }}
            
            .ticket-total-line {{
                margin-bottom: 3px;
            }}
            
            .ticket-footer {{
                text-align: center;
                margin-top: 15px;
                font-size: 10px;
                color: #666;
            }}
        }}
        
        /* Estilos para vista previa en pantalla */
        body {{
            font-family: 'Courier New', monospace;
            font-size: 12px;
            margin: 0;
            padding: 10px;
            width: 300px;
            background: white;
            color: black;
            border: 1px solid #ccc;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .ticket-header {{
            text-align: center;
            border-bottom: 1px dashed #000;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }}
        
        .ticket-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .ticket-subtitle {{
            font-size: 10px;
            color: #666;
        }}
        
        .ticket-info {{
            margin-bottom: 10px;
        }}
        
        .ticket-items {{
            border-bottom: 1px dashed #000;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }}
        
        .ticket-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 3px;
        }}
        
        .ticket-item-name {{
            flex: 1;
        }}
        
        .ticket-item-qty {{
            text-align: center;
            margin: 0 5px;
        }}
        
        .ticket-item-price {{
            text-align: right;
            margin-left: 5px;
        }}
        
        .ticket-totals {{
            text-align: right;
        }}
        
        .ticket-total-line {{
            margin-bottom: 3px;
        }}
        
        .ticket-footer {{
            text-align: center;
            margin-top: 15px;
            font-size: 10px;
            color: #666;
        }}
        </style>
    </head>
    <body>
        <div class="ticket-header">
            <div class="ticket-title">SISTEMA POS</div>
            <div class="ticket-subtitle">Punto de Venta</div>
        </div>
        
        <div class="ticket-info">
            <div><strong>Ticket:</strong> {sale.sale_number}</div>
            <div><strong>Fecha:</strong> {sale.created_at.strftime('%d/%m/%Y %H:%M')}</div>
            <div><strong>Cliente:</strong> {customer_name}</div>
            <div><strong>Vendedor:</strong> {current_user.full_name}</div>
        </div>
        
        <div class="ticket-items">
            <div style="border-bottom: 1px solid #000; margin-bottom: 5px; padding-bottom: 3px;">
                <strong>PRODUCTOS</strong>
            </div>
    """
    
    for item, product_name, product_code in items:
        html_content += f"""
            <div class="ticket-item">
                <div class="ticket-item-name">{product_name}</div>
                <div class="ticket-item-qty">{item.quantity}</div>
                <div class="ticket-item-price">${item.unit_price:.2f}</div>
            </div>
            <div style="text-align: right; font-size: 10px; color: #666; margin-bottom: 5px;">
                {product_code} - ${item.total:.2f}
            </div>
        """
    
    subtotal = float(sale.total) / 1.16  # Asumiendo 16% IVA
    tax = float(sale.total) - subtotal
    
    html_content += f"""
        </div>
        
        <div class="ticket-totals">
            <div class="ticket-total-line">
                <span>Subtotal:</span>
                <span style="margin-left: 20px;">${subtotal:.2f}</span>
            </div>
            <div class="ticket-total-line">
                <span>IVA (16%):</span>
                <span style="margin-left: 20px;">${tax:.2f}</span>
            </div>
            <div class="ticket-total-line" style="border-top: 1px solid #000; padding-top: 5px; font-weight: bold;">
                <span>TOTAL:</span>
                <span style="margin-left: 20px;">${sale.total:.2f}</span>
            </div>
        </div>
        
        <div class="ticket-footer">
            <div>¡Gracias por su compra!</div>
            <div>Vuelva pronto</div>
        </div>
    </body>
    </html>
    """
    
    return Response(content=html_content, media_type="text/html")