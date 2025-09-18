"""
Servicio para el sistema de menú del día
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc
from datetime import date, datetime
from decimal import Decimal
import asyncio

from app.models.menu import MenuDayOld, CategoriaMenu, OpcionMenu, MenuStatus
from app.models.order import Order, OrderItem
from app.schemas.menu import MenuDayCreate, OpcionMenuCreate, CategoriaMenuCreate


class MenuService:
    """Servicio para gestionar el sistema de menú del día"""
    
    @staticmethod
    def create_menu_day(db: Session, menu_data: MenuDayCreate) -> MenuDayOld:
        """Crear un nuevo menú del día"""
        # Verificar si ya existe un menú para esa fecha
        existing_menu = db.query(MenuDayOld).filter(MenuDayOld.fecha == menu_data.fecha).first()
        if existing_menu:
            raise ValueError(f"Ya existe un menú para la fecha {menu_data.fecha}")
        
        # Crear el menú
        menu = MenuDayOld(
            fecha=menu_data.fecha,
            nombre=menu_data.nombre,
            precio=menu_data.precio,
            descripcion=menu_data.descripcion,
            estado=menu_data.estado
        )
        
        db.add(menu)
        db.flush()  # Para obtener el ID
        
        # Agregar opciones
        for opcion_data in menu_data.opciones:
            opcion = OpcionMenu(
                menu_id=menu.id,
                categoria_id=opcion_data.categoria_id,
                nombre=opcion_data.nombre,
                descripcion=opcion_data.descripcion,
                is_active=opcion_data.is_active
            )
            db.add(opcion)
        
        db.commit()
        db.refresh(menu)
        return menu
    
    @staticmethod
    def get_menu_by_date(db: Session, fecha: date) -> Optional[MenuDayOld]:
        """Obtener menú por fecha"""
        return db.query(MenuDayOld).options(
            joinedload(MenuDayOld.opciones).joinedload(OpcionMenu.categoria)
        ).filter(
            and_(
                MenuDayOld.fecha == fecha,
                MenuDayOld.estado == MenuStatus.ACTIVE
            )
        ).first()
    
    @staticmethod
    def get_today_menu(db: Session) -> Optional[MenuDayOld]:
        """Obtener menú del día actual"""
        return MenuService.get_menu_by_date(db, date.today())
    
    @staticmethod
    def get_all_menus(db: Session, limit: int = 10) -> List[MenuDayOld]:
        """Obtener todos los menús ordenados por fecha"""
        return db.query(MenuDayOld).options(
            joinedload(MenuDayOld.opciones).joinedload(OpcionMenu.categoria)
        ).order_by(desc(MenuDayOld.fecha)).limit(limit).all()
    
    @staticmethod
    def create_categoria(db: Session, categoria_data: CategoriaMenuCreate) -> CategoriaMenu:
        """Crear una nueva categoría de menú"""
        categoria = CategoriaMenu(
            nombre=categoria_data.nombre,
            orden=categoria_data.orden,
            descripcion=categoria_data.descripcion,
            is_active=categoria_data.is_active
        )
        
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria
    
    @staticmethod
    def get_all_categorias(db: Session) -> List[CategoriaMenu]:
        """Obtener todas las categorías activas ordenadas"""
        return db.query(CategoriaMenu).filter(
            CategoriaMenu.is_active == True
        ).order_by(CategoriaMenu.orden).all()
    
    @staticmethod
    def get_categoria_by_id(db: Session, categoria_id: int) -> Optional[CategoriaMenu]:
        """Obtener categoría por ID"""
        return db.query(CategoriaMenu).filter(CategoriaMenu.id == categoria_id).first()
    
    @staticmethod
    def add_opcion_to_menu(db: Session, menu_id: int, opcion_data: OpcionMenuCreate) -> OpcionMenu:
        """Agregar opción a un menú existente"""
        # Verificar que el menú existe
        menu = db.query(MenuDayOld).filter(MenuDayOld.id == menu_id).first()
        if not menu:
            raise ValueError(f"Menú con ID {menu_id} no encontrado")
        
        # Verificar que la categoría existe
        categoria = db.query(CategoriaMenu).filter(CategoriaMenu.id == opcion_data.categoria_id).first()
        if not categoria:
            raise ValueError(f"Categoría con ID {opcion_data.categoria_id} no encontrada")
        
        opcion = OpcionMenu(
            menu_id=menu_id,
            categoria_id=opcion_data.categoria_id,
            nombre=opcion_data.nombre,
            descripcion=opcion_data.descripcion,
            is_active=opcion_data.is_active
        )
        
        db.add(opcion)
        db.commit()
        db.refresh(opcion)
        return opcion
    
    @staticmethod
    def get_menu_with_categories(db: Session, menu_id: int) -> Optional[Dict]:
        """Obtener menú con opciones agrupadas por categoría"""
        menu = db.query(MenuDayOld).options(
            joinedload(MenuDayOld.opciones).joinedload(OpcionMenu.categoria)
        ).filter(MenuDayOld.id == menu_id).first()
        
        if not menu:
            return None
        
        # Agrupar opciones por categoría
        opciones_por_categoria = {}
        for opcion in menu.opciones:
            if opcion.is_active:
                cat_nombre = opcion.categoria.nombre
                if cat_nombre not in opciones_por_categoria:
                    opciones_por_categoria[cat_nombre] = {
                        'categoria': {
                            'id': opcion.categoria.id,
                            'nombre': opcion.categoria.nombre,
                            'orden': opcion.categoria.orden,
                            'descripcion': opcion.categoria.descripcion
                        },
                        'opciones': []
                    }
                opciones_por_categoria[cat_nombre]['opciones'].append({
                    'id': opcion.id,
                    'nombre': opcion.nombre,
                    'descripcion': opcion.descripcion
                })
        
        return {
            'menu': {
                'id': menu.id,
                'fecha': menu.fecha,
                'nombre': menu.nombre,
                'precio': menu.precio,
                'descripcion': menu.descripcion,
                'estado': menu.estado
            },
            'opciones_por_categoria': opciones_por_categoria
        }
    
    @staticmethod
    def create_order_with_menu_items(
        db: Session, 
        waiter_id: int,
        table_id: Optional[int],
        menu_items: List[Dict],
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Order:
        """Crear pedido con items de menú"""
        # Verificar que el menú existe y está activo
        if not menu_items:
            raise ValueError("Debe incluir al menos un item de menú")
        
        menu_id = menu_items[0]['menu_id']
        menu = db.query(MenuDayOld).filter(
            and_(
                MenuDayOld.id == menu_id,
                MenuDayOld.estado == MenuStatus.ACTIVE
            )
        ).first()
        
        if not menu:
            raise ValueError(f"Menú con ID {menu_id} no encontrado o inactivo")
        
        # Crear el pedido
        order = Order(
            table_id=table_id,
            waiter_id=waiter_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            notes=notes,
            estado_cocina='Pendiente'
        )
        
        db.add(order)
        db.flush()  # Para obtener el ID
        
        # Agregar items del menú
        total_amount = Decimal('0.00')
        for item_data in menu_items:
            # Verificar que la opción existe
            opcion = db.query(OpcionMenu).filter(
                and_(
                    OpcionMenu.id == item_data['opcion_id'],
                    OpcionMenu.menu_id == menu_id,
                    OpcionMenu.is_active == True
                )
            ).first()
            
            if not opcion:
                raise ValueError(f"Opción con ID {item_data['opcion_id']} no encontrada")
            
            # Crear item del pedido
            order_item = OrderItem(
                order_id=order.id,
                menu_id=menu_id,
                categoria_id=item_data['categoria_id'],
                opcion_id=item_data['opcion_id'],
                quantity=item_data['quantity'],
                unit_price=menu.precio,
                total_price=menu.precio * item_data['quantity'],
                observaciones=item_data.get('observaciones')
            )
            
            db.add(order_item)
            total_amount += order_item.total_price
        
        # Calcular totales del pedido
        order.total_amount = total_amount
        order.tax_amount = total_amount * Decimal('0.19')  # 19% IVA
        order.final_amount = order.total_amount + order.tax_amount
        
        db.commit()
        db.refresh(order)
        
        # Notificar nuevo pedido vía WebSocket
        try:
            from app.websocket_manager import WebSocketEvents
            order_data = {
                "id": order.id,
                "order_number": order.order_number,
                "table_number": order.table.table_number if order.table else "N/A",
                "waiter_name": order.waiter.full_name if order.waiter else "N/A",
                "items_count": len(order.items),
                "total_amount": order.total_amount,
                "created_at": order.created_at.isoformat()
            }
            # Ejecutar notificación de forma asíncrona
            asyncio.create_task(WebSocketEvents.notify_new_order(order_data))
        except Exception as e:
            print(f"⚠️ Error enviando notificación WebSocket: {e}")
        
        return order
    
    @staticmethod
    def get_orders_by_estado_cocina(db: Session, estado: str) -> List[Order]:
        """Obtener pedidos por estado de cocina"""
        return db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.menu),
            joinedload(Order.items).joinedload(OrderItem.categoria),
            joinedload(Order.items).joinedload(OrderItem.opcion),
            joinedload(Order.table),
            joinedload(Order.waiter)
        ).filter(Order.estado_cocina == estado).order_by(Order.created_at).all()
    
    @staticmethod
    def update_order_estado_cocina(db: Session, order_id: int, nuevo_estado: str) -> Optional[Order]:
        """Actualizar estado de cocina de un pedido"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        
        estado_anterior = order.estado_cocina
        order.estado_cocina = nuevo_estado
        db.commit()
        db.refresh(order)
        
        # Notificar cambio de estado vía WebSocket
        try:
            from app.websocket_manager import WebSocketEvents
            order_data = {
                "id": order.id,
                "order_number": order.order_number,
                "estado_anterior": estado_anterior,
                "estado_nuevo": nuevo_estado,
                "table_number": order.table.table_number if order.table else "N/A",
                "waiter_name": order.waiter.full_name if order.waiter else "N/A",
                "updated_at": order.updated_at.isoformat() if order.updated_at else datetime.now().isoformat()
            }
            # Ejecutar notificación de forma asíncrona
            asyncio.create_task(WebSocketEvents.notify_order_status_change(order_data))
        except Exception as e:
            print(f"⚠️ Error enviando notificación WebSocket: {e}")
        
        return order
