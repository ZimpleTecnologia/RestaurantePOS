"""
Servicio para generación de reportes avanzados del restaurante
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

from app.models.order import Order, OrderItem, OrderStatus
from app.models.sale import Sale, SaleItem, SaleStatus
from app.models.product import Product
from app.models.user import User, UserRole
from app.models.location import Table
from app.models.inventory import InventoryMovement, MovementType


class ReportService:
    """Servicio para generación de reportes"""
    
    @staticmethod
    def get_sales_report(
        db: Session,
        start_date: date,
        end_date: date,
        group_by: str = "day",
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Reporte de ventas por período"""
        
        # Construir query base
        query = db.query(Sale).filter(
            and_(
                Sale.created_at >= datetime.combine(start_date, datetime.min.time()),
                Sale.created_at <= datetime.combine(end_date, datetime.max.time()),
                Sale.status == SaleStatus.COMPLETED
            )
        )
        
        # Filtrar por usuario si se especifica
        if user_id:
            query = query.filter(Sale.user_id == user_id)
        
        # Agrupar por período
        if group_by == "day":
            sales_data = query.with_entities(
                func.date(Sale.created_at).label('date'),
                func.count(Sale.id).label('total_sales'),
                func.sum(Sale.total).label('total_revenue'),
                func.avg(Sale.total).label('avg_sale')
            ).group_by(func.date(Sale.created_at)).order_by(asc('date')).all()
        elif group_by == "hour":
            sales_data = query.with_entities(
                func.extract('hour', Sale.created_at).label('hour'),
                func.count(Sale.id).label('total_sales'),
                func.sum(Sale.total).label('total_revenue')
            ).group_by(func.extract('hour', Sale.created_at)).order_by(asc('hour')).all()
        else:  # month
            sales_data = query.with_entities(
                func.date_trunc('month', Sale.created_at).label('month'),
                func.count(Sale.id).label('total_sales'),
                func.sum(Sale.total).label('total_revenue')
            ).group_by(func.date_trunc('month', Sale.created_at)).order_by(asc('month')).all()
        
        # Estadísticas generales
        total_sales = query.count()
        total_revenue = query.with_entities(func.sum(Sale.total)).scalar() or 0
        avg_sale = total_revenue / total_sales if total_sales > 0 else 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "group_by": group_by
            },
            "summary": {
                "total_sales": total_sales,
                "total_revenue": float(total_revenue),
                "average_sale": float(avg_sale)
            },
            "data": [
                {
                    "period": str(item.date) if group_by == "day" else str(item.hour) if group_by == "hour" else str(item.month),
                    "sales_count": item.total_sales,
                    "revenue": float(item.total_revenue),
                    "avg_sale": float(item.avg_sale) if hasattr(item, 'avg_sale') else 0
                }
                for item in sales_data
            ]
        }
    
    @staticmethod
    def get_top_products_report(
        db: Session,
        start_date: date,
        end_date: date,
        limit: int = 10,
        by_quantity: bool = True
    ) -> List[Dict[str, Any]]:
        """Reporte de productos más vendidos"""
        
        # Query base para items vendidos
        query = db.query(
            Product.name,
            Product.category,
            func.sum(SaleItem.quantity).label('total_quantity'),
            func.sum(SaleItem.total_price).label('total_revenue'),
            func.count(SaleItem.id).label('sale_count')
        ).join(SaleItem).join(Sale).filter(
            and_(
                Sale.created_at >= datetime.combine(start_date, datetime.min.time()),
                Sale.created_at <= datetime.combine(end_date, datetime.max.time()),
                Sale.status == SaleStatus.COMPLETED
            )
        ).group_by(Product.id, Product.name, Product.category)
        
        # Ordenar por cantidad o ingresos
        if by_quantity:
            query = query.order_by(desc('total_quantity'))
        else:
            query = query.order_by(desc('total_revenue'))
        
        products = query.limit(limit).all()
        
        return [
            {
                "product_name": product.name,
                "category": product.category,
                "total_quantity": int(product.total_quantity),
                "total_revenue": float(product.total_revenue),
                "sale_count": product.sale_count,
                "avg_price": float(product.total_revenue / product.total_quantity) if product.total_quantity > 0 else 0
            }
            for product in products
        ]
    
    @staticmethod
    def get_waiter_performance_report(
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Reporte de rendimiento por mesero"""
        
        # Obtener estadísticas por mesero
        waiter_stats = db.query(
            User.full_name,
            User.username,
            func.count(Order.id).label('total_orders'),
            func.sum(Order.final_amount).label('total_sales'),
            func.avg(Order.final_amount).label('avg_order'),
            func.count(Order.id).filter(Order.status == OrderStatus.PAID).label('completed_orders'),
            func.count(Order.id).filter(Order.status == OrderStatus.CANCELLED).label('cancelled_orders')
        ).join(Order).filter(
            and_(
                Order.created_at >= datetime.combine(start_date, datetime.min.time()),
                Order.created_at <= datetime.combine(end_date, datetime.max.time()),
                User.role == UserRole.MESERO
            )
        ).group_by(User.id, User.full_name, User.username).all()
        
        return [
            {
                "waiter_name": waiter.full_name,
                "username": waiter.username,
                "total_orders": waiter.total_orders,
                "total_sales": float(waiter.total_sales),
                "average_order": float(waiter.avg_order),
                "completed_orders": waiter.completed_orders,
                "cancelled_orders": waiter.cancelled_orders,
                "completion_rate": (waiter.completed_orders / waiter.total_orders * 100) if waiter.total_orders > 0 else 0
            }
            for waiter in waiter_stats
        ]
    
    @staticmethod
    def get_table_performance_report(
        db: Session,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Reporte de rendimiento por mesa"""
        
        table_stats = db.query(
            Table.table_number,
            func.count(Order.id).label('total_orders'),
            func.sum(Order.final_amount).label('total_revenue'),
            func.avg(Order.final_amount).label('avg_order'),
            func.avg(func.extract('epoch', Order.paid_at - Order.created_at) / 3600).label('avg_turnover_hours')
        ).join(Order).filter(
            and_(
                Order.created_at >= datetime.combine(start_date, datetime.min.time()),
                Order.created_at <= datetime.combine(end_date, datetime.max.time()),
                Order.status == OrderStatus.PAID
            )
        ).group_by(Table.id, Table.table_number).all()
        
        return [
            {
                "table_number": table.table_number,
                "total_orders": table.total_orders,
                "total_revenue": float(table.total_revenue),
                "average_order": float(table.avg_order),
                "average_turnover_hours": float(table.avg_turnover_hours) if table.avg_turnover_hours else 0,
                "daily_revenue": float(table.total_revenue) / ((end_date - start_date).days + 1)
            }
            for table in table_stats
        ]
    
    @staticmethod
    def get_inventory_movement_report(
        db: Session,
        start_date: date,
        end_date: date,
        movement_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reporte de movimientos de inventario"""
        
        query = db.query(InventoryMovement).filter(
            and_(
                InventoryMovement.created_at >= datetime.combine(start_date, datetime.min.time()),
                InventoryMovement.created_at <= datetime.combine(end_date, datetime.max.time())
            )
        )
        
        if movement_type:
            query = query.filter(InventoryMovement.movement_type == movement_type)
        
        movements = query.all()
        
        # Agrupar por tipo de movimiento
        movement_summary = {}
        for movement in movements:
            movement_type = movement.movement_type
            if movement_type not in movement_summary:
                movement_summary[movement_type] = {
                    "count": 0,
                    "total_quantity": 0,
                    "total_value": 0
                }
            
            movement_summary[movement_type]["count"] += 1
            movement_summary[movement_type]["total_quantity"] += movement.quantity
            movement_summary[movement_type]["total_value"] += float(movement.quantity * (movement.unit_cost or 0))
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_movements": len(movements),
            "movement_summary": movement_summary,
            "movements": [
                {
                    "id": movement.id,
                    "product_name": movement.product.name,
                    "movement_type": movement.movement_type,
                    "quantity": movement.quantity,
                    "unit_cost": float(movement.unit_cost) if movement.unit_cost else 0,
                    "total_value": float(movement.quantity * (movement.unit_cost or 0)),
                    "reason": movement.reason,
                    "created_at": movement.created_at.isoformat(),
                    "user_name": movement.user.full_name if movement.user else "Sistema"
                }
                for movement in movements
            ]
        }
    
    @staticmethod
    def get_daily_summary_report(db: Session, report_date: date) -> Dict[str, Any]:
        """Resumen diario completo del restaurante"""
        
        start_datetime = datetime.combine(report_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)
        
        # Estadísticas de órdenes
        orders_query = db.query(Order).filter(
            Order.created_at >= start_datetime,
            Order.created_at < end_datetime
        )
        
        total_orders = orders_query.count()
        completed_orders = orders_query.filter(Order.status == OrderStatus.PAID).count()
        cancelled_orders = orders_query.filter(Order.status == OrderStatus.CANCELLED).count()
        
        # Ingresos por tipo de pedido
        revenue_by_type = db.query(
            Order.order_type,
            func.sum(Order.final_amount).label('total_revenue'),
            func.count(Order.id).label('order_count')
        ).filter(
            Order.created_at >= start_datetime,
            Order.created_at < end_datetime,
            Order.status == OrderStatus.PAID
        ).group_by(Order.order_type).all()
        
        # Tiempo promedio de preparación
        prep_times = db.query(
            func.extract('epoch', Order.kitchen_end_time - Order.kitchen_start_time).label('prep_time')
        ).filter(
            Order.created_at >= start_datetime,
            Order.created_at < end_datetime,
            Order.kitchen_start_time.isnot(None),
            Order.kitchen_end_time.isnot(None)
        ).all()
        
        avg_prep_time = 0
        if prep_times:
            avg_prep_time = sum([pt.prep_time for pt in prep_times]) / len(prep_times) / 60
        
        # Productos más vendidos del día
        top_products = db.query(
            Product.name,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.total_price).label('total_revenue')
        ).join(OrderItem).join(Order).filter(
            Order.created_at >= start_datetime,
            Order.created_at < end_datetime,
            Order.status == OrderStatus.PAID
        ).group_by(Product.id, Product.name).order_by(
            desc(func.sum(OrderItem.quantity))
        ).limit(5).all()
        
        # Rendimiento por mesero
        waiter_performance = db.query(
            User.full_name,
            func.count(Order.id).label('orders_count'),
            func.sum(Order.final_amount).label('total_sales')
        ).join(Order).filter(
            Order.created_at >= start_datetime,
            Order.created_at < end_datetime,
            Order.status == OrderStatus.PAID
        ).group_by(User.id, User.full_name).all()
        
        return {
            "date": report_date.isoformat(),
            "orders": {
                "total": total_orders,
                "completed": completed_orders,
                "cancelled": cancelled_orders,
                "completion_rate": (completed_orders / total_orders * 100) if total_orders > 0 else 0
            },
            "revenue": {
                "by_type": [
                    {
                        "type": item.order_type,
                        "revenue": float(item.total_revenue),
                        "count": item.order_count
                    }
                    for item in revenue_by_type
                ],
                "total": sum(float(item.total_revenue) for item in revenue_by_type)
            },
            "performance": {
                "avg_prep_time_minutes": round(avg_prep_time, 2),
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
                        "name": waiter.full_name,
                        "orders": waiter.orders_count,
                        "sales": float(waiter.total_sales)
                    }
                    for waiter in waiter_performance
                ]
            }
        }
    
    @staticmethod
    def export_to_excel_format(report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Formatear datos para exportación a Excel"""
        # Esta función prepara los datos en un formato adecuado para exportación
        # En una implementación real, usarías openpyxl para crear el archivo Excel
        
        return {
            "filename": f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "sheets": {
                "Resumen": report_data.get("summary", {}),
                "Detalles": report_data.get("data", []),
                "Gráficos": report_data.get("charts", {})
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": report_data.get("type", "unknown"),
                "period": report_data.get("period", {})
            }
        }
