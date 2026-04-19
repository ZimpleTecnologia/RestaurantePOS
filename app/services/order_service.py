"""
Servicio para el manejo de pedidos del restaurante
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.order import Order, OrderItem, OrderStatus, OrderType
from app.models.location import Table, TableStatus
from app.models.product import Product


class OrderService:
    """Servicio para manejo de pedidos"""
    
    @staticmethod
    def generate_order_number(db: Session) -> str:
        """Generar número único de pedido"""
        today = datetime.now().strftime('%Y%m%d')
        
        # Contar pedidos del día
        order_count = db.query(Order).filter(
            func.date(Order.created_at) == datetime.now().date()
        ).count()
        
        return f"P{today}-{order_count + 1:03d}"
    
    @staticmethod
    def create_order(
        db: Session,
        waiter_id: int,
        table_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        order_type: OrderType = OrderType.DINE_IN,
        status: OrderStatus = OrderStatus.DRAFT,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Order:
        """Crear un nuevo pedido"""
        order = Order(
            order_number=OrderService.generate_order_number(db),
            table_id=table_id,
            waiter_id=waiter_id,
            customer_id=customer_id,
            order_type=order_type,
            status=status,
            customer_name=customer_name,
            customer_phone=customer_phone,
            notes=notes
        )
        
        db.add(order)
        db.flush()  # Para obtener el ID
        
        # Si es pedido en mesa y no es borrador, ocupar la mesa
        if table_id and order_type == OrderType.DINE_IN and status != OrderStatus.DRAFT:
            TableService.occupy_table(db, table_id)
        
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def add_item_to_order(
        db: Session,
        order_id: int,
        item_type: str = "product",
        product_id: Optional[int] = None,
        menu_id: Optional[int] = None,
        plato_id: Optional[int] = None,
        quantity: int = 1,
        unit_price: Optional[Decimal] = None,
        notes: Optional[str] = None,
        special_instructions: Optional[str] = None,
        opciones: Optional[List[Dict[str, Any]]] = None
    ) -> OrderItem:
        """Agregar item a un pedido con soporte para menús y platos"""
        from app.models.order import OrderItemOption
        from app.models.restaurant_menu import MenuDia, PlatoRestaurante
        
        item = OrderItem(
            order_id=order_id,
            item_type=item_type,
            product_id=product_id,
            menu_id=menu_id,
            plato_id=plato_id,
            quantity=quantity,
            notes=notes,
            special_instructions=special_instructions
        )
        
        # Obtener información según el tipo e item
        if item_type == "product" and product_id:
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product: raise ValueError(f"Producto {product_id} no encontrado")
            item.unit_price = unit_price or product.precio_base
            item.create_snapshot()
            
        elif item_type == "menu" and menu_id:
            menu = db.query(MenuDia).filter(MenuDia.id == menu_id).first()
            if not menu: raise ValueError(f"Menú {menu_id} no encontrado")
            item.unit_price = unit_price or menu.precio
            item.snapshot_name = menu.nombre
            item.snapshot_description = menu.descripcion
            item.snapshot_price = menu.precio
            
        elif item_type == "plato" and plato_id:
            plato = db.query(PlatoRestaurante).filter(PlatoRestaurante.id == plato_id).first()
            if not plato: raise ValueError(f"Plato {plato_id} no encontrado")
            item.unit_price = unit_price or plato.precio
            item.create_snapshot()
            
        if item.unit_price is None:
            item.unit_price = Decimal('0.00')

        # Calcular precio total
        item.calculate_total()
        db.add(item)
        db.flush()
        
        # Agregar opciones si existen
        if opciones:
            for opt in opciones:
                db_opt = OrderItemOption(
                    order_item_id=item.id,
                    categoria=opt.get('categoria'),
                    opcion_elegida=opt.get('opcion_elegida'),
                    opcion_plato_id=opt.get('opcion_plato_id')
                )
                db.add(db_opt)

        db.commit()
        db.refresh(item)
        
        # Recalcular totales del pedido
        order = OrderService.get_order_by_id(db, order_id)
        if order:
            order.calculate_totals()
            db.commit()
        
        return item
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
        """Obtener pedido por ID"""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
        """Obtener pedido por número"""
        return db.query(Order).filter(Order.order_number == order_number).first()
    
    @staticmethod
    def get_active_orders(db: Session) -> List[Order]:
        """Obtener pedidos activos"""
        return db.query(Order).filter(Order.is_active == True).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_pending_orders(db: Session) -> List[Order]:
        """Obtener pedidos pendientes (para cocina)"""
        return db.query(Order).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING])
        ).order_by(Order.created_at.asc()).all()
    
    @staticmethod
    def get_ready_orders(db: Session) -> List[Order]:
        """Obtener pedidos listos para servir"""
        return db.query(Order).filter(Order.status == OrderStatus.READY).order_by(Order.created_at.asc()).all()
    
    @staticmethod
    def get_pending_payment_orders(db: Session) -> List[Order]:
        """Obtener pedidos pendientes de pago"""
        return db.query(Order).filter(Order.status == OrderStatus.SERVED).order_by(Order.created_at.asc()).all()
    
    @staticmethod
    def update_order_status(db: Session, order_id: int, status: OrderStatus) -> Optional[Order]:
        """Actualizar estado de un pedido"""
        order = OrderService.get_order_by_id(db, order_id)
        if order:
            order.status = status
            
            # Actualizar timestamps específicos
            if status == OrderStatus.SERVED:
                order.served_at = datetime.now()
            elif status == OrderStatus.PAID:
                order.paid_at = datetime.now()
                # Liberar mesa si es pedido en mesa
                if order.table_id and order.order_type == OrderType.DINE_IN:
                    TableService.free_table(db, order.table_id)
            
            db.commit()
            db.refresh(order)
        return order
    
    @staticmethod
    def mark_order_as_preparing(db: Session, order_id: int) -> Optional[Order]:
        """Marcar pedido como en preparación"""
        return OrderService.update_order_status(db, order_id, OrderStatus.PREPARING)
    
    @staticmethod
    def mark_order_as_ready(db: Session, order_id: int) -> Optional[Order]:
        """Marcar pedido como listo"""
        return OrderService.update_order_status(db, order_id, OrderStatus.READY)
    
    @staticmethod
    def mark_order_as_served(db: Session, order_id: int) -> Optional[Order]:
        """Marcar pedido como servido"""
        return OrderService.update_order_status(db, order_id, OrderStatus.SERVED)
    
    @staticmethod
    def mark_order_as_paid(db: Session, order_id: int) -> Optional[Order]:
        """Marcar pedido como pagado"""
        return OrderService.update_order_status(db, order_id, OrderStatus.PAID)
    
    @staticmethod
    def cancel_order(db: Session, order_id: int) -> Optional[Order]:
        """Cancelar un pedido"""
        order = OrderService.get_order_by_id(db, order_id)
        if order and order.status not in [OrderStatus.PAID, OrderStatus.CANCELLED]:
            # Liberar mesa si es pedido en mesa
            if order.table_id and order.order_type == OrderType.DINE_IN:
                TableService.free_table(db, order.table_id)
            
            return OrderService.update_order_status(db, order_id, OrderStatus.CANCELLED)
        return order
    
    @staticmethod
    def get_order_details(db: Session, order_id: int) -> Optional[Dict[str, Any]]:
        """Obtener detalles completos de un pedido"""
        order = OrderService.get_order_by_id(db, order_id)
        if not order:
            return None
        
        return {
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "status": order.status,
                "order_type": order.order_type,
                "total_amount": float(order.total_amount),
                "tax_amount": float(order.tax_amount),
                "discount_amount": float(order.discount_amount),
                "final_amount": float(order.final_amount),
                "notes": order.notes,
                "created_at": order.created_at,
                "served_at": order.served_at,
                "paid_at": order.paid_at
            },
            "table": {
                "id": order.table.id,
                "table_number": order.table.table_number,
                "name": order.table.name,
                "location": order.table.location
            } if order.table else None,
            "waiter": {
                "id": order.waiter.id,
                "name": order.waiter.full_name,
                "username": order.waiter.username
            },
            "customer": {
                "id": order.customer.id,
                "name": order.customer.full_name,
                "phone": order.customer.phone
            } if order.customer else None,
            "items": [
                {
                    "id": item.id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "total_price": float(item.total_price),
                    "notes": item.notes,
                    "special_instructions": item.special_instructions,
                    "is_ready": item.is_ready,
                    "is_served": item.is_served
                }
                for item in order.items
            ]
        }
    
    @staticmethod
    def get_orders_summary(db: Session) -> Dict[str, Any]:
        """Obtener resumen de pedidos"""
        total_orders = db.query(Order).filter(
            func.date(Order.created_at) == datetime.now().date()
        ).count()
        
        pending_orders = db.query(Order).filter(
            and_(
                func.date(Order.created_at) == datetime.now().date(),
                Order.status.in_([OrderStatus.PENDING, OrderStatus.PREPARING])
            )
        ).count()
        
        ready_orders = db.query(Order).filter(
            and_(
                func.date(Order.created_at) == datetime.now().date(),
                Order.status == OrderStatus.READY
            )
        ).count()
        
        served_orders = db.query(Order).filter(
            and_(
                func.date(Order.created_at) == datetime.now().date(),
                Order.status == OrderStatus.SERVED
            )
        ).count()
        
        paid_orders = db.query(Order).filter(
            and_(
                func.date(Order.created_at) == datetime.now().date(),
                Order.status == OrderStatus.PAID
            )
        ).count()
        
        total_revenue = db.query(func.sum(Order.final_amount)).filter(
            and_(
                func.date(Order.created_at) == datetime.now().date(),
                Order.status == OrderStatus.PAID
            )
        ).scalar() or Decimal('0.00')
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "ready_orders": ready_orders,
            "served_orders": served_orders,
            "paid_orders": paid_orders,
            "total_revenue": float(total_revenue)
        }


# Importar TableService para evitar dependencias circulares
from app.services.table_service import TableService
