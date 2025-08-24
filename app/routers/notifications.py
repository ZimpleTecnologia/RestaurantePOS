"""
Router para sistema de notificaciones en tiempo real
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.location import Table
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["notificaciones"])


class NotificationService:
    """Servicio para gestionar notificaciones"""
    
    @staticmethod
    def get_waiter_notifications(db: Session, waiter_id: int) -> List[dict]:
        """Obtener notificaciones para meseros"""
        notifications = []
        
        # Órdenes listas para servir
        ready_orders = db.query(Order).filter(
            Order.waiter_id == waiter_id,
            Order.status == OrderStatus.LISTO
        ).all()
        
        for order in ready_orders:
            notifications.append({
                "id": f"order_ready_{order.id}",
                "type": "order_ready",
                "title": "Orden Lista",
                "message": f"Orden {order.order_number} lista para servir en Mesa {order.table.table_number}",
                "order_id": order.id,
                "table_id": order.table_id,
                "priority": "high",
                "created_at": order.kitchen_end_time or order.updated_at,
                "icon": "check-circle",
                "color": "success"
            })
        
        # Mesas que han estado ocupadas por mucho tiempo sin órdenes
        occupied_tables = db.query(Table).join(Order).filter(
            Order.waiter_id == waiter_id,
            Order.status == OrderStatus.SERVIDO,
            Order.served_time < datetime.now() - timedelta(hours=1)
        ).all()
        
        for table in occupied_tables:
            notifications.append({
                "id": f"table_check_{table.id}",
                "type": "table_check",
                "title": "Revisar Mesa",
                "message": f"Mesa {table.table_number} necesita atención",
                "table_id": table.id,
                "priority": "medium",
                "created_at": datetime.now(),
                "icon": "clock",
                "color": "warning"
            })
        
        return sorted(notifications, key=lambda x: x["created_at"], reverse=True)
    
    @staticmethod
    def get_kitchen_notifications(db: Session) -> List[dict]:
        """Obtener notificaciones para cocina"""
        notifications = []
        
        # Órdenes pendientes por mucho tiempo
        old_orders = db.query(Order).filter(
            Order.status == OrderStatus.PENDIENTE,
            Order.created_at < datetime.now() - timedelta(minutes=15)
        ).all()
        
        for order in old_orders:
            notifications.append({
                "id": f"order_delayed_{order.id}",
                "type": "order_delayed",
                "title": "Orden Retrasada",
                "message": f"Orden {order.order_number} lleva más de 15 minutos sin iniciar",
                "order_id": order.id,
                "priority": "high",
                "created_at": order.created_at,
                "icon": "exclamation-triangle",
                "color": "danger"
            })
        
        # Órdenes urgentes
        urgent_orders = db.query(Order).filter(
            Order.priority == "urgente",
            Order.status.in_([OrderStatus.PENDIENTE, OrderStatus.EN_PREPARACION])
        ).all()
        
        for order in urgent_orders:
            notifications.append({
                "id": f"order_urgent_{order.id}",
                "type": "order_urgent",
                "title": "Orden Urgente",
                "message": f"Orden {order.order_number} marcada como urgente",
                "order_id": order.id,
                "priority": "urgent",
                "created_at": order.created_at,
                "icon": "lightning",
                "color": "danger"
            })
        
        return sorted(notifications, key=lambda x: x["created_at"], reverse=True)
    
    @staticmethod
    def get_cashier_notifications(db: Session) -> List[dict]:
        """Obtener notificaciones para caja"""
        notifications = []
        
        # Órdenes servidas pendientes de pago
        unpaid_orders = db.query(Order).filter(
            Order.status == OrderStatus.SERVIDO,
            Order.served_time < datetime.now() - timedelta(minutes=30)
        ).all()
        
        for order in unpaid_orders:
            notifications.append({
                "id": f"payment_pending_{order.id}",
                "type": "payment_pending", 
                "title": "Pago Pendiente",
                "message": f"Mesa {order.table.table_number} tiene orden servida sin pagar",
                "order_id": order.id,
                "table_id": order.table_id,
                "priority": "medium",
                "created_at": order.served_time,
                "icon": "cash",
                "color": "warning"
            })
        
        return sorted(notifications, key=lambda x: x["created_at"], reverse=True)


@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener notificaciones según el rol del usuario"""
    
    if current_user.role == UserRole.MESERO:
        notifications = NotificationService.get_waiter_notifications(db, current_user.id)
    elif current_user.role == UserRole.COCINA:
        notifications = NotificationService.get_kitchen_notifications(db)
    elif current_user.role == UserRole.CAJA:
        notifications = NotificationService.get_cashier_notifications(db)
    elif current_user.role == UserRole.ADMIN:
        # Admin ve todas las notificaciones
        waiter_notifs = NotificationService.get_waiter_notifications(db, current_user.id)
        kitchen_notifs = NotificationService.get_kitchen_notifications(db)
        cashier_notifs = NotificationService.get_cashier_notifications(db)
        notifications = waiter_notifs + kitchen_notifs + cashier_notifs
    else:
        notifications = []
    
    return {
        "notifications": notifications,
        "count": len(notifications),
        "unread_count": len([n for n in notifications if n["priority"] in ["high", "urgent"]])
    }


@router.get("/count")
def get_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener solo el conteo de notificaciones"""
    
    if current_user.role == UserRole.MESERO:
        notifications = NotificationService.get_waiter_notifications(db, current_user.id)
    elif current_user.role == UserRole.COCINA:
        notifications = NotificationService.get_kitchen_notifications(db)
    elif current_user.role == UserRole.CAJA:
        notifications = NotificationService.get_cashier_notifications(db)
    else:
        notifications = []
    
    return {
        "total_count": len(notifications),
        "high_priority": len([n for n in notifications if n["priority"] == "high"]),
        "urgent_count": len([n for n in notifications if n["priority"] == "urgent"])
    }


@router.get("/stats")
def get_restaurant_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas generales del restaurante"""
    
    # Estadísticas de órdenes
    total_orders_today = db.query(Order).filter(
        Order.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    pending_orders = db.query(Order).filter(
        Order.status == OrderStatus.PENDIENTE
    ).count()
    
    preparing_orders = db.query(Order).filter(
        Order.status == OrderStatus.EN_PREPARACION
    ).count()
    
    ready_orders = db.query(Order).filter(
        Order.status == OrderStatus.LISTO
    ).count()
    
    # Tiempo promedio de preparación hoy
    completed_orders = db.query(Order).filter(
        Order.status == OrderStatus.SERVIDO,
        Order.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        Order.kitchen_start_time.isnot(None),
        Order.kitchen_end_time.isnot(None)
    ).all()
    
    avg_prep_time = 0
    if completed_orders:
        total_time = sum([
            (order.kitchen_end_time - order.kitchen_start_time).total_seconds()
            for order in completed_orders
        ])
        avg_prep_time = total_time / len(completed_orders) / 60  # en minutos
    
    # Estadísticas de mesas
    from app.models.location import TableStatus
    total_tables = db.query(Table).filter(Table.is_active == True).count()
    occupied_tables = db.query(Table).filter(
        Table.status == TableStatus.OCUPADA,
        Table.is_active == True
    ).count()
    
    return {
        "orders": {
            "total_today": total_orders_today,
            "pending": pending_orders,
            "preparing": preparing_orders,
            "ready": ready_orders,
            "avg_prep_time_minutes": round(avg_prep_time, 1)
        },
        "tables": {
            "total": total_tables,
            "occupied": occupied_tables,
            "free": total_tables - occupied_tables,
            "occupancy_rate": round((occupied_tables / total_tables * 100) if total_tables > 0 else 0, 1)
        },
        "timestamp": datetime.now()
    }
