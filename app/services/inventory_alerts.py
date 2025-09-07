"""
Servicio para manejo de alertas de inventario
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

from app.models.product import Product
from app.models.inventory import InventoryMovement, MovementType
from app.models.notifications import Notification, NotificationType
from app.models.user import User, UserRole


class InventoryAlertService:
    """Servicio para manejo de alertas de inventario"""
    
    @staticmethod
    def check_low_stock_products(db: Session) -> List[Dict[str, Any]]:
        """Verificar productos con stock bajo"""
        products = db.query(Product).filter(
            and_(
                Product.track_stock == True,
                Product.is_active == True,
                Product.stock_quantity <= Product.min_stock_level
            )
        ).all()
        
        alerts = []
        for product in products:
            alert = {
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": product.stock_quantity,
                "min_stock": product.min_stock_level,
                "unit": product.unit,
                "alert_type": "low_stock" if product.stock_quantity > 0 else "out_of_stock",
                "message": product.get_stock_alert_message(),
                "needs_reorder": product.needs_reorder,
                "supplier_name": product.supplier.name if product.supplier else None
            }
            alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def check_expiring_products(db: Session, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Verificar productos próximos a caducar"""
        from app.models.inventory import InventoryLot
        
        expiration_date = datetime.now().date() + timedelta(days=days_ahead)
        
        lots = db.query(InventoryLot).filter(
            and_(
                InventoryLot.expiration_date <= expiration_date,
                InventoryLot.expiration_date >= datetime.now().date(),
                InventoryLot.available_quantity > 0,
                InventoryLot.is_active == True
            )
        ).all()
        
        alerts = []
        for lot in lots:
            days_to_expire = (lot.expiration_date - datetime.now().date()).days
            
            alert = {
                "product_id": lot.product.id,
                "product_name": lot.product.name,
                "lot_number": lot.lot_number,
                "expiration_date": lot.expiration_date.isoformat(),
                "days_to_expire": days_to_expire,
                "available_quantity": lot.available_quantity,
                "unit": lot.product.unit,
                "alert_type": "expiring_soon",
                "message": f"⚠️ {lot.product.name} (Lote {lot.lot_number}) caduca en {days_to_expire} días",
                "urgency": "high" if days_to_expire <= 3 else "medium"
            }
            alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def check_overstock_products(db: Session) -> List[Dict[str, Any]]:
        """Verificar productos con sobrestock"""
        products = db.query(Product).filter(
            and_(
                Product.track_stock == True,
                Product.is_active == True,
                Product.max_stock_level > 0,
                Product.stock_quantity > Product.max_stock_level
            )
        ).all()
        
        alerts = []
        for product in products:
            alert = {
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": product.stock_quantity,
                "max_stock": product.max_stock_level,
                "unit": product.unit,
                "alert_type": "overstock",
                "message": f"📦 {product.name} tiene sobrestock ({product.stock_quantity} > {product.max_stock_level} {product.unit})",
                "excess_quantity": product.stock_quantity - product.max_stock_level
            }
            alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def check_slow_moving_products(db: Session, days_threshold: int = 30) -> List[Dict[str, Any]]:
        """Verificar productos de movimiento lento"""
        from app.models.sale import SaleItem
        
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        # Obtener productos que no han tenido ventas recientes
        recent_sales = db.query(SaleItem.product_id).filter(
            SaleItem.created_at >= threshold_date
        ).distinct().all()
        
        recent_product_ids = [sale[0] for sale in recent_sales]
        
        slow_products = db.query(Product).filter(
            and_(
                Product.track_stock == True,
                Product.is_active == True,
                Product.stock_quantity > 0,
                ~Product.id.in_(recent_product_ids)
            )
        ).all()
        
        alerts = []
        for product in slow_products:
            # Obtener última venta
            last_sale = db.query(SaleItem).filter(
                SaleItem.product_id == product.id
            ).order_by(SaleItem.created_at.desc()).first()
            
            days_since_last_sale = None
            if last_sale:
                days_since_last_sale = (datetime.now() - last_sale.created_at).days
            
            alert = {
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": product.stock_quantity,
                "unit": product.unit,
                "alert_type": "slow_moving",
                "message": f"🐌 {product.name} no se ha vendido en {days_since_last_sale or 'mucho tiempo'} días",
                "days_since_last_sale": days_since_last_sale,
                "stock_value": float(product.stock_quantity * (product.cost_price or 0))
            }
            alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def create_inventory_notifications(db: Session, alerts: List[Dict[str, Any]]) -> List[Notification]:
        """Crear notificaciones para alertas de inventario"""
        notifications = []
        
        # Obtener usuarios que deben recibir notificaciones
        users = db.query(User).filter(
            User.role.in_([UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR])
        ).all()
        
        for alert in alerts:
            for user in users:
                notification = Notification(
                    user_id=user.id,
                    type=NotificationType.INVENTORY_ALERT,
                    title=f"Alerta de Inventario: {alert['alert_type'].replace('_', ' ').title()}",
                    message=alert['message'],
                    data=alert,
                    is_read=False
                )
                notifications.append(notification)
        
        db.add_all(notifications)
        db.commit()
        
        return notifications
    
    @staticmethod
    def get_inventory_dashboard_data(db: Session) -> Dict[str, Any]:
        """Obtener datos para el dashboard de inventario"""
        # Productos con stock bajo
        low_stock_count = db.query(Product).filter(
            and_(
                Product.track_stock == True,
                Product.stock_quantity <= Product.min_stock_level,
                Product.stock_quantity > 0
            )
        ).count()
        
        # Productos agotados
        out_of_stock_count = db.query(Product).filter(
            and_(
                Product.track_stock == True,
                Product.stock_quantity <= 0
            )
        ).count()
        
        # Productos con sobrestock
        overstock_count = db.query(Product).filter(
            and_(
                Product.track_stock == True,
                Product.max_stock_level > 0,
                Product.stock_quantity > Product.max_stock_level
            )
        ).count()
        
        # Productos que necesitan reorden
        reorder_count = db.query(Product).filter(
            and_(
                Product.track_stock == True,
                Product.stock_quantity <= Product.reorder_point
            )
        ).count()
        
        # Valor total del inventario
        total_value = db.query(Product).filter(
            Product.track_stock == True
        ).all()
        
        inventory_value = sum(
            product.stock_quantity * (product.cost_price or 0) 
            for product in total_value
        )
        
        return {
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "overstock_count": overstock_count,
            "reorder_count": reorder_count,
            "inventory_value": float(inventory_value),
            "total_products": len(total_value)
        }
    
    @staticmethod
    def generate_reorder_suggestions(db: Session) -> List[Dict[str, Any]]:
        """Generar sugerencias de reorden"""
        products = db.query(Product).filter(
            and_(
                Product.track_stock == True,
                Product.needs_reorder == True,
                Product.is_active == True
            )
        ).all()
        
        suggestions = []
        for product in products:
            # Calcular cantidad sugerida de reorden
            suggested_quantity = max(
                product.max_stock_level - product.stock_quantity,
                product.reorder_point - product.stock_quantity + 10  # Buffer de seguridad
            )
            
            suggestion = {
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": product.stock_quantity,
                "reorder_point": product.reorder_point,
                "max_stock": product.max_stock_level,
                "suggested_quantity": suggested_quantity,
                "unit": product.unit,
                "supplier_name": product.supplier.name if product.supplier else None,
                "supplier_contact": product.supplier.phone if product.supplier else None,
                "estimated_cost": float(suggested_quantity * (product.cost_price or 0))
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    @staticmethod
    def process_barcode_scan(db: Session, barcode: str) -> Dict[str, Any]:
        """Procesar escaneo de código de barras"""
        product = db.query(Product).filter(Product.barcode == barcode).first()
        
        if not product:
            return {
                "success": False,
                "message": "Producto no encontrado",
                "barcode": barcode
            }
        
        if not product.is_active:
            return {
                "success": False,
                "message": "Producto inactivo",
                "product_name": product.name
            }
        
        # Verificar stock si aplica
        stock_info = None
        if product.track_stock:
            stock_info = {
                "current_stock": product.stock_quantity,
                "unit": product.unit,
                "is_low_stock": product.is_low_stock,
                "is_out_of_stock": product.is_out_of_stock,
                "alert_message": product.get_stock_alert_message()
            }
        
        return {
            "success": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "category": product.category,
                "image_url": product.image_url,
                "stock_info": stock_info
            }
        }
