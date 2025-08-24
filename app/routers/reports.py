"""
Router para reportes específicos del restaurante
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus, OrderItem
from app.models.sale import Sale, SaleStatus
from app.models.product import Product
from app.models.location import Table
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["reportes"])


@router.get("/daily-summary")
def get_daily_summary(
    report_date: Optional[date] = Query(default=None, description="Fecha del reporte (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resumen diario del restaurante"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.CAJA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver reportes"
        )
    
    if not report_date:
        report_date = date.today()
    
    start_date = datetime.combine(report_date, datetime.min.time())
    end_date = start_date + timedelta(days=1)
    
    # Estadísticas de órdenes
    orders_query = db.query(Order).filter(
        Order.created_at >= start_date,
        Order.created_at < end_date
    )
    
    total_orders = orders_query.count()
    completed_orders = orders_query.filter(Order.status == OrderStatus.SERVIDO).count()
    cancelled_orders = orders_query.filter(Order.status == OrderStatus.CANCELADO).count()
    
    # Tiempo promedio de preparación
    prep_times = db.query(
        func.extract('epoch', Order.kitchen_end_time - Order.kitchen_start_time).label('prep_time')
    ).filter(
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Order.kitchen_start_time.isnot(None),
        Order.kitchen_end_time.isnot(None)
    ).all()
    
    avg_prep_time = 0
    if prep_times:
        avg_prep_time = sum([pt.prep_time for pt in prep_times]) / len(prep_times) / 60
    
    # Estadísticas de ventas
    sales_query = db.query(Sale).filter(
        Sale.created_at >= start_date,
        Sale.created_at < end_date
    )
    
    total_sales = sales_query.filter(Sale.status == SaleStatus.COMPLETADA).count()
    total_revenue = db.query(func.sum(Sale.total)).filter(
        Sale.created_at >= start_date,
        Sale.created_at < end_date,
        Sale.status == SaleStatus.COMPLETADA
    ).scalar() or 0
    
    # Productos más vendidos
    top_products = db.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.subtotal).label('total_revenue')
    ).join(OrderItem).join(Order).filter(
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Order.status == OrderStatus.SERVIDO
    ).group_by(Product.id, Product.name).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()
    
    # Rendimiento por mesero
    waiter_performance = db.query(
        User.full_name,
        func.count(Order.id).label('orders_count'),
        func.sum(Sale.total).label('total_sales')
    ).join(Order, User.id == Order.waiter_id).join(Sale, Order.sale_id == Sale.id).filter(
        Order.created_at >= start_date,
        Order.created_at < end_date,
        Sale.status == SaleStatus.COMPLETADA
    ).group_by(User.id, User.full_name).all()
    
    # Distribución por horas
    hourly_distribution = db.query(
        func.extract('hour', Order.created_at).label('hour'),
        func.count(Order.id).label('orders_count')
    ).filter(
        Order.created_at >= start_date,
        Order.created_at < end_date
    ).group_by(func.extract('hour', Order.created_at)).order_by('hour').all()
    
    return {
        "date": report_date,
        "summary": {
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "completion_rate": round((completed_orders / total_orders * 100) if total_orders > 0 else 0, 1),
            "total_sales": total_sales,
            "total_revenue": float(total_revenue),
            "avg_prep_time_minutes": round(avg_prep_time, 1)
        },
        "top_products": [
            {
                "name": product.name,
                "quantity": int(product.total_quantity),
                "revenue": float(product.total_revenue)
            }
            for product in top_products
        ],
        "waiter_performance": [
            {
                "waiter_name": waiter.full_name,
                "orders_count": int(waiter.orders_count),
                "total_sales": float(waiter.total_sales or 0)
            }
            for waiter in waiter_performance
        ],
        "hourly_distribution": [
            {
                "hour": int(hour.hour),
                "orders_count": int(hour.orders_count)
            }
            for hour in hourly_distribution
        ]
    }


@router.get("/kitchen-performance")
def get_kitchen_performance(
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reporte de rendimiento de cocina"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.COCINA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este reporte"
        )
    
    if not start_date:
        start_date = date.today() - timedelta(days=7)
    if not end_date:
        end_date = date.today()
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Órdenes completadas
    completed_orders = db.query(Order).filter(
        Order.created_at >= start_datetime,
        Order.created_at <= end_datetime,
        Order.status == OrderStatus.SERVIDO,
        Order.kitchen_start_time.isnot(None),
        Order.kitchen_end_time.isnot(None)
    ).all()
    
    # Calcular métricas
    if not completed_orders:
        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "metrics": {
                "total_orders": 0,
                "avg_prep_time": 0,
                "min_prep_time": 0,
                "max_prep_time": 0,
                "orders_under_15_min": 0,
                "orders_over_30_min": 0
            },
            "daily_breakdown": []
        }
    
    prep_times = []
    for order in completed_orders:
        prep_time = (order.kitchen_end_time - order.kitchen_start_time).total_seconds() / 60
        prep_times.append(prep_time)
    
    avg_prep_time = sum(prep_times) / len(prep_times)
    min_prep_time = min(prep_times)
    max_prep_time = max(prep_times)
    orders_under_15 = len([t for t in prep_times if t <= 15])
    orders_over_30 = len([t for t in prep_times if t > 30])
    
    # Desglose diario
    daily_breakdown = {}
    for order in completed_orders:
        day = order.created_at.date()
        if day not in daily_breakdown:
            daily_breakdown[day] = []
        
        prep_time = (order.kitchen_end_time - order.kitchen_start_time).total_seconds() / 60
        daily_breakdown[day].append(prep_time)
    
    daily_stats = []
    for day, times in daily_breakdown.items():
        daily_stats.append({
            "date": day,
            "orders_count": len(times),
            "avg_prep_time": round(sum(times) / len(times), 1),
            "min_prep_time": round(min(times), 1),
            "max_prep_time": round(max(times), 1)
        })
    
    daily_stats.sort(key=lambda x: x["date"])
    
    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "metrics": {
            "total_orders": len(completed_orders),
            "avg_prep_time": round(avg_prep_time, 1),
            "min_prep_time": round(min_prep_time, 1),
            "max_prep_time": round(max_prep_time, 1),
            "orders_under_15_min": orders_under_15,
            "orders_over_30_min": orders_over_30,
            "efficiency_rate": round((orders_under_15 / len(completed_orders) * 100), 1)
        },
        "daily_breakdown": daily_stats
    }


@router.get("/waiter-performance")
def get_waiter_performance(
    waiter_id: Optional[int] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reporte de rendimiento de meseros"""
    
    # Los meseros solo pueden ver su propio rendimiento
    if current_user.role == UserRole.MESERO:
        waiter_id = current_user.id
    elif current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este reporte"
        )
    
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Query base
    query = db.query(
        User.id,
        User.full_name,
        func.count(Order.id).label('total_orders'),
        func.count(func.nullif(Order.status == OrderStatus.SERVIDO, False)).label('completed_orders'),
        func.count(func.nullif(Order.status == OrderStatus.CANCELADO, False)).label('cancelled_orders'),
        func.sum(Sale.total).label('total_sales'),
        func.avg(func.extract('epoch', Order.served_time - Order.created_at) / 60).label('avg_service_time')
    ).join(Order, User.id == Order.waiter_id).outerjoin(Sale, Order.sale_id == Sale.id).filter(
        Order.created_at >= start_datetime,
        Order.created_at <= end_datetime
    )
    
    if waiter_id:
        query = query.filter(User.id == waiter_id)
        result = query.group_by(User.id, User.full_name).first()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mesero no encontrado o sin datos en el período"
            )
        
        # Desglose diario para el mesero específico
        daily_orders = db.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('orders_count'),
            func.sum(Sale.total).label('daily_sales')
        ).join(Sale, Order.sale_id == Sale.id).filter(
            Order.waiter_id == waiter_id,
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime,
            Sale.status == SaleStatus.COMPLETADA
        ).group_by(func.date(Order.created_at)).order_by('date').all()
        
        return {
            "waiter": {
                "id": result.id,
                "name": result.full_name,
                "total_orders": int(result.total_orders),
                "completed_orders": int(result.completed_orders or 0),
                "cancelled_orders": int(result.cancelled_orders or 0),
                "completion_rate": round((result.completed_orders / result.total_orders * 100) if result.total_orders > 0 else 0, 1),
                "total_sales": float(result.total_sales or 0),
                "avg_service_time_minutes": round(result.avg_service_time or 0, 1)
            },
            "daily_breakdown": [
                {
                    "date": day.date,
                    "orders_count": int(day.orders_count),
                    "daily_sales": float(day.daily_sales or 0)
                }
                for day in daily_orders
            ],
            "period": {"start_date": start_date, "end_date": end_date}
        }
    
    else:
        # Ranking de todos los meseros
        results = query.group_by(User.id, User.full_name).order_by(
            func.sum(Sale.total).desc()
        ).all()
        
        return {
            "waiters": [
                {
                    "id": waiter.id,
                    "name": waiter.full_name,
                    "total_orders": int(waiter.total_orders),
                    "completed_orders": int(waiter.completed_orders or 0),
                    "cancelled_orders": int(waiter.cancelled_orders or 0),
                    "completion_rate": round((waiter.completed_orders / waiter.total_orders * 100) if waiter.total_orders > 0 else 0, 1),
                    "total_sales": float(waiter.total_sales or 0),
                    "avg_service_time_minutes": round(waiter.avg_service_time or 0, 1)
                }
                for waiter in results
            ],
            "period": {"start_date": start_date, "end_date": end_date}
        }


@router.get("/table-turnover")
def get_table_turnover(
    report_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reporte de rotación de mesas"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este reporte"
        )
    
    if not report_date:
        report_date = date.today()
    
    start_date = datetime.combine(report_date, datetime.min.time())
    end_date = start_date + timedelta(days=1)
    
    # Estadísticas por mesa
    table_stats = db.query(
        Table.id,
        Table.table_number,
        Table.capacity,
        func.count(Order.id).label('total_orders'),
        func.sum(func.extract('epoch', Order.served_time - Order.created_at) / 60).label('total_occupation_time'),
        func.avg(func.extract('epoch', Order.served_time - Order.created_at) / 60).label('avg_occupation_time'),
        func.sum(Sale.total).label('total_revenue')
    ).outerjoin(Order, Table.id == Order.table_id).outerjoin(Sale, Order.sale_id == Sale.id).filter(
        or_(Order.created_at == None, and_(
            Order.created_at >= start_date,
            Order.created_at < end_date,
            Order.status == OrderStatus.SERVIDO
        ))
    ).group_by(Table.id, Table.table_number, Table.capacity).all()
    
    # Calcular métricas
    table_data = []
    for table in table_stats:
        turnover_rate = 0
        revenue_per_hour = 0
        
        if table.total_orders and table.total_occupation_time:
            # Horas de operación (asumimos 12 horas)
            operating_hours = 12 * 60  # en minutos
            turnover_rate = (table.total_orders * table.avg_occupation_time) / operating_hours
            revenue_per_hour = (table.total_revenue or 0) / (table.total_occupation_time / 60)
        
        table_data.append({
            "table_id": table.id,
            "table_number": table.table_number,
            "capacity": table.capacity,
            "total_orders": int(table.total_orders or 0),
            "avg_occupation_time_minutes": round(table.avg_occupation_time or 0, 1),
            "turnover_rate": round(turnover_rate, 2),
            "total_revenue": float(table.total_revenue or 0),
            "revenue_per_hour": round(revenue_per_hour, 2)
        })
    
    # Ordenar por ingresos totales
    table_data.sort(key=lambda x: x["total_revenue"], reverse=True)
    
    # Estadísticas generales
    total_orders = sum([t["total_orders"] for t in table_data])
    total_revenue = sum([t["total_revenue"] for t in table_data])
    avg_turnover = sum([t["turnover_rate"] for t in table_data]) / len(table_data) if table_data else 0
    
    return {
        "date": report_date,
        "summary": {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "avg_turnover_rate": round(avg_turnover, 2),
            "most_profitable_table": table_data[0]["table_number"] if table_data else None
        },
        "tables": table_data
    }
