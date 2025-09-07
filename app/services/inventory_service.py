"""
Servicios de inventario profesionalizados
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, desc, asc
from sqlalchemy.exc import IntegrityError
import logging

from app.models.inventory import (
    InventoryMovement, InventoryLot, InventoryLocation, 
    InventoryAlert, InventoryCount, InventoryCountItem,
    MovementType, MovementReason
)
from app.models.product import Product
from app.models.user import User
from app.schemas.inventory import (
    InventoryMovementCreate, InventoryLotCreate, InventoryLocationCreate,
    InventoryAlertCreate, InventoryCountCreate, InventoryCountItemCreate,
    StockTransfer, BulkStockAdjustment, InventorySearchFilters
)

logger = logging.getLogger(__name__)


class InventoryService:
    """Servicio principal de inventario"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== UBICACIONES ====================
    
    def create_location(self, location_data: InventoryLocationCreate) -> InventoryLocation:
        """Crear nueva ubicación de inventario"""
        try:
            # Si es ubicación por defecto, desactivar otras
            if location_data.is_default:
                self.db.query(InventoryLocation).filter(
                    InventoryLocation.is_default == True
                ).update({"is_default": False})
            
            location = InventoryLocation(**location_data.dict())
            self.db.add(location)
            self.db.commit()
            self.db.refresh(location)
            
            logger.info(f"Ubicación creada: {location.name}")
            return location
            
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe una ubicación con ese nombre")
    
    def get_locations(self, active_only: bool = True) -> List[InventoryLocation]:
        """Obtener ubicaciones de inventario"""
        query = self.db.query(InventoryLocation)
        if active_only:
            query = query.filter(InventoryLocation.is_active == True)
        return query.order_by(InventoryLocation.name).all()
    
    def get_default_location(self) -> Optional[InventoryLocation]:
        """Obtener ubicación por defecto"""
        return self.db.query(InventoryLocation).filter(
            InventoryLocation.is_default == True,
            InventoryLocation.is_active == True
        ).first()
    
    # ==================== LOTES ====================
    
    def create_lot(self, lot_data: InventoryLotCreate) -> InventoryLot:
        """Crear nuevo lote de inventario"""
        try:
            # Verificar que el producto existe
            product = self.db.query(Product).filter(Product.id == lot_data.product_id).first()
            if not product:
                raise ValueError("Producto no encontrado")
            
            # Verificar que la ubicación existe
            location = self.db.query(InventoryLocation).filter(
                InventoryLocation.id == lot_data.location_id
            ).first()
            if not location:
                raise ValueError("Ubicación no encontrada")
            
            # Calcular cantidad disponible
            available_quantity = lot_data.quantity - lot_data.quantity * 0  # Sin reservas iniciales
            
            lot = InventoryLot(
                **lot_data.dict(),
                available_quantity=available_quantity,
                reserved_quantity=0,
                total_cost=lot_data.unit_cost * lot_data.quantity if lot_data.unit_cost else None
            )
            
            self.db.add(lot)
            self.db.commit()
            self.db.refresh(lot)
            
            # Actualizar stock del producto
            self._update_product_stock(lot_data.product_id)
            
            logger.info(f"Lote creado: {lot.lot_number} para producto {product.name}")
            return lot
            
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un lote con ese número")
    
    def get_product_lots(self, product_id: int, active_only: bool = True) -> List[InventoryLot]:
        """Obtener lotes de un producto"""
        query = self.db.query(InventoryLot).filter(InventoryLot.product_id == product_id)
        if active_only:
            query = query.filter(InventoryLot.is_active == True)
        return query.order_by(desc(InventoryLot.expiration_date)).all()
    
    def get_expiring_lots(self, days: int = 30) -> List[InventoryLot]:
        """Obtener lotes próximos a expirar"""
        expiry_date = date.today() + timedelta(days=days)
        return self.db.query(InventoryLot).filter(
            and_(
                InventoryLot.expiration_date <= expiry_date,
                InventoryLot.expiration_date >= date.today(),
                InventoryLot.available_quantity > 0,
                InventoryLot.is_active == True
            )
        ).order_by(InventoryLot.expiration_date).all()
    
    def get_expired_lots(self) -> List[InventoryLot]:
        """Obtener lotes expirados"""
        return self.db.query(InventoryLot).filter(
            and_(
                InventoryLot.expiration_date < date.today(),
                InventoryLot.available_quantity > 0,
                InventoryLot.is_active == True
            )
        ).order_by(InventoryLot.expiration_date).all()
    
    # ==================== MOVIMIENTOS ====================
    
    def create_movement(self, movement_data: InventoryMovementCreate, user_id: int) -> InventoryMovement:
        """Crear movimiento de inventario"""
        try:
            # Verificar que el producto existe
            product = self.db.query(Product).filter(Product.id == movement_data.product_id).first()
            if not product:
                raise ValueError("Producto no encontrado")
            
            # Obtener stock actual
            previous_stock = product.stock
            
            # Calcular nuevo stock
            if movement_data.movement_type in [MovementType.ENTRADA, MovementType.DEVOLUCION, MovementType.AJUSTE]:
                new_stock = previous_stock + movement_data.quantity
            else:
                new_stock = previous_stock - movement_data.quantity
                if new_stock < 0:
                    raise ValueError("Stock insuficiente para realizar el movimiento")
            
            # Crear movimiento
            movement = InventoryMovement(
                **movement_data.dict(),
                user_id=user_id,
                previous_stock=previous_stock,
                new_stock=new_stock,
                total_cost=movement_data.unit_cost * movement_data.quantity if movement_data.unit_cost else None
            )
            
            self.db.add(movement)
            
            # Actualizar stock del producto
            product.stock = new_stock
            
            # Si hay lote específico, actualizar lote
            if movement_data.lot_id:
                lot = self.db.query(InventoryLot).filter(InventoryLot.id == movement_data.lot_id).first()
                if lot:
                    if movement_data.movement_type in [MovementType.ENTRADA, MovementType.DEVOLUCION]:
                        lot.quantity += movement_data.quantity
                        lot.available_quantity += movement_data.quantity
                    else:
                        lot.quantity -= movement_data.quantity
                        lot.available_quantity -= movement_data.quantity
            
            self.db.commit()
            self.db.refresh(movement)
            
            # Crear alertas si es necesario
            self._check_and_create_alerts(product.id, new_stock)
            
            logger.info(f"Movimiento creado: {movement.movement_type} - {movement.quantity} unidades")
            return movement
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creando movimiento: {str(e)}")
            raise
    
    def bulk_adjustment(self, adjustments: BulkStockAdjustment, user_id: int) -> List[InventoryMovement]:
        """Ajuste masivo de stock"""
        movements = []
        
        try:
            for adjustment in adjustments.adjustments:
                movement = self.create_movement(adjustment, user_id)
                movements.append(movement)
            
            self.db.commit()
            logger.info(f"Ajuste masivo completado: {len(movements)} movimientos")
            return movements
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error en ajuste masivo: {str(e)}")
            raise
    
    def transfer_stock(self, transfer_data: StockTransfer, user_id: int) -> Tuple[InventoryMovement, InventoryMovement]:
        """Transferir stock entre ubicaciones"""
        try:
            # Verificar stock disponible
            if transfer_data.lot_id:
                lot = self.db.query(InventoryLot).filter(InventoryLot.id == transfer_data.lot_id).first()
                if not lot or lot.available_quantity < transfer_data.quantity:
                    raise ValueError("Stock insuficiente en el lote para la transferencia")
            else:
                product = self.db.query(Product).filter(Product.id == transfer_data.product_id).first()
                if not product or product.stock < transfer_data.quantity:
                    raise ValueError("Stock insuficiente para la transferencia")
            
            # Crear movimiento de salida
            exit_movement = InventoryMovement(
                product_id=transfer_data.product_id,
                lot_id=transfer_data.lot_id,
                location_id=transfer_data.from_location_id,
                user_id=user_id,
                movement_type=MovementType.TRANSFERENCIA,
                reason=MovementReason.TRANSFERENCIA_SALIDA,
                quantity=transfer_data.quantity,
                previous_stock=product.stock if not transfer_data.lot_id else lot.quantity,
                new_stock=(product.stock if not transfer_data.lot_id else lot.quantity) - transfer_data.quantity,
                notes=f"Transferencia a ubicación {transfer_data.to_location_id}",
                reference_type="transfer",
                reference_number=f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            # Crear movimiento de entrada
            entry_movement = InventoryMovement(
                product_id=transfer_data.product_id,
                lot_id=transfer_data.lot_id,
                location_id=transfer_data.to_location_id,
                user_id=user_id,
                movement_type=MovementType.TRANSFERENCIA,
                reason=MovementReason.TRANSFERENCIA_ENTRADA,
                quantity=transfer_data.quantity,
                previous_stock=(product.stock if not transfer_data.lot_id else lot.quantity) - transfer_data.quantity,
                new_stock=product.stock if not transfer_data.lot_id else lot.quantity,
                notes=f"Transferencia desde ubicación {transfer_data.from_location_id}",
                reference_type="transfer",
                reference_number=f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            self.db.add(exit_movement)
            self.db.add(entry_movement)
            
            # Actualizar lotes si es necesario
            if transfer_data.lot_id:
                lot.quantity -= transfer_data.quantity
                lot.available_quantity -= transfer_data.quantity
                
                # Buscar o crear lote en destino
                dest_lot = self.db.query(InventoryLot).filter(
                    and_(
                        InventoryLot.product_id == transfer_data.product_id,
                        InventoryLot.location_id == transfer_data.to_location_id,
                        InventoryLot.lot_number == lot.lot_number
                    )
                ).first()
                
                if dest_lot:
                    dest_lot.quantity += transfer_data.quantity
                    dest_lot.available_quantity += transfer_data.quantity
                else:
                    # Crear nuevo lote en destino
                    new_lot = InventoryLot(
                        product_id=transfer_data.product_id,
                        location_id=transfer_data.to_location_id,
                        lot_number=lot.lot_number,
                        batch_number=lot.batch_number,
                        supplier_lot=lot.supplier_lot,
                        quantity=transfer_data.quantity,
                        available_quantity=transfer_data.quantity,
                        unit_cost=lot.unit_cost,
                        manufacturing_date=lot.manufacturing_date,
                        expiration_date=lot.expiration_date,
                        supplier_id=lot.supplier_id
                    )
                    self.db.add(new_lot)
            
            self.db.commit()
            self.db.refresh(exit_movement)
            self.db.refresh(entry_movement)
            
            logger.info(f"Transferencia completada: {transfer_data.quantity} unidades")
            return exit_movement, entry_movement
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error en transferencia: {str(e)}")
            raise
    
    def get_movements(self, filters: Dict[str, Any] = None, limit: int = 100, offset: int = 0) -> List[InventoryMovement]:
        """Obtener movimientos con filtros"""
        query = self.db.query(InventoryMovement).options(
            joinedload(InventoryMovement.product),
            joinedload(InventoryMovement.lot),
            joinedload(InventoryMovement.user),
            joinedload(InventoryMovement.location)
        )
        
        if filters:
            if filters.get('product_id'):
                query = query.filter(InventoryMovement.product_id == filters['product_id'])
            if filters.get('movement_type'):
                query = query.filter(InventoryMovement.movement_type == filters['movement_type'])
            if filters.get('start_date'):
                query = query.filter(InventoryMovement.created_at >= filters['start_date'])
            if filters.get('end_date'):
                query = query.filter(InventoryMovement.created_at <= filters['end_date'])
            if filters.get('user_id'):
                query = query.filter(InventoryMovement.user_id == filters['user_id'])
        
        return query.order_by(desc(InventoryMovement.created_at)).offset(offset).limit(limit).all()
    
    # ==================== ALERTAS ====================
    
    def _check_and_create_alerts(self, product_id: int, current_stock: int):
        """Verificar y crear alertas automáticas"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return
        
        # Alerta de stock bajo
        if current_stock <= product.min_stock and current_stock > 0:
            self._create_alert(
                product_id=product_id,
                alert_type="low_stock",
                alert_level="warning" if current_stock > 0 else "critical",
                message=f"Stock bajo para {product.name}: {current_stock} unidades (mínimo: {product.min_stock})"
            )
        
        # Alerta de stock agotado
        elif current_stock == 0:
            self._create_alert(
                product_id=product_id,
                alert_type="out_of_stock",
                alert_level="critical",
                message=f"Stock agotado para {product.name}"
            )
        
        # Alerta de sobrestock
        elif current_stock >= product.max_stock:
            self._create_alert(
                product_id=product_id,
                alert_type="overstock",
                alert_level="info",
                message=f"Sobrestock para {product.name}: {current_stock} unidades (máximo: {product.max_stock})"
            )
    
    def _create_alert(self, product_id: int, alert_type: str, alert_level: str, message: str, lot_id: int = None):
        """Crear alerta de inventario"""
        # Verificar si ya existe una alerta activa del mismo tipo
        existing_alert = self.db.query(InventoryAlert).filter(
            and_(
                InventoryAlert.product_id == product_id,
                InventoryAlert.alert_type == alert_type,
                InventoryAlert.is_active == True,
                InventoryAlert.lot_id == lot_id
            )
        ).first()
        
        if not existing_alert:
            alert = InventoryAlert(
                product_id=product_id,
                lot_id=lot_id,
                alert_type=alert_type,
                alert_level=alert_level,
                message=message
            )
            self.db.add(alert)
            self.db.commit()
            logger.info(f"Alerta creada: {alert_type} para producto {product_id}")
    
    def get_active_alerts(self, alert_type: str = None) -> List[InventoryAlert]:
        """Obtener alertas activas"""
        query = self.db.query(InventoryAlert).filter(InventoryAlert.is_active == True)
        if alert_type:
            query = query.filter(InventoryAlert.alert_type == alert_type)
        return query.order_by(desc(InventoryAlert.created_at)).all()
    
    def acknowledge_alert(self, alert_id: int, user_id: int):
        """Reconocer alerta"""
        alert = self.db.query(InventoryAlert).filter(InventoryAlert.id == alert_id).first()
        if alert:
            alert.is_acknowledged = True
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.now()
            self.db.commit()
            logger.info(f"Alerta reconocida: {alert_id}")
    
    # ==================== CONTEOS FÍSICOS ====================
    
    def create_count(self, count_data: InventoryCountCreate, user_id: int) -> InventoryCount:
        """Crear conteo físico"""
        try:
            count = InventoryCount(
                **count_data.dict(),
                created_by=user_id
            )
            self.db.add(count)
            self.db.commit()
            self.db.refresh(count)
            
            logger.info(f"Conteo físico creado: {count.count_number}")
            return count
            
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ya existe un conteo con ese número")
    
    def add_count_item(self, item_data: InventoryCountItemCreate) -> InventoryCountItem:
        """Agregar item a conteo físico"""
        # Verificar que el conteo existe y está en estado draft
        count = self.db.query(InventoryCount).filter(InventoryCount.id == item_data.count_id).first()
        if not count:
            raise ValueError("Conteo no encontrado")
        if count.status != "draft":
            raise ValueError("Solo se pueden agregar items a conteos en borrador")
        
        # Verificar que no existe ya el item
        existing_item = self.db.query(InventoryCountItem).filter(
            and_(
                InventoryCountItem.count_id == item_data.count_id,
                InventoryCountItem.product_id == item_data.product_id,
                InventoryCountItem.lot_id == item_data.lot_id
            )
        ).first()
        
        if existing_item:
            raise ValueError("El item ya existe en este conteo")
        
        item = InventoryCountItem(**item_data.dict())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        
        return item
    
    def complete_count(self, count_id: int, user_id: int) -> InventoryCount:
        """Completar conteo físico y generar ajustes"""
        count = self.db.query(InventoryCount).filter(InventoryCount.id == count_id).first()
        if not count:
            raise ValueError("Conteo no encontrado")
        
        if count.status != "in_progress":
            raise ValueError("El conteo debe estar en progreso para completarlo")
        
        # Procesar cada item del conteo
        for item in count.count_items:
            if item.actual_quantity is not None:
                variance = item.actual_quantity - item.expected_quantity
                if variance != 0:
                    # Crear ajuste de inventario
                    movement_data = InventoryMovementCreate(
                        product_id=item.product_id,
                        lot_id=item.lot_id,
                        location_id=count.location_id,
                        movement_type=MovementType.INVENTARIO_FISICO,
                        reason=MovementReason.AJUSTE_POSITIVO if variance > 0 else MovementReason.AJUSTE_NEGATIVO,
                        quantity=abs(variance),
                        notes=f"Ajuste por conteo físico {count.count_number}"
                    )
                    
                    self.create_movement(movement_data, user_id)
        
        # Marcar conteo como completado
        count.status = "completed"
        count.completed_at = datetime.now()
        self.db.commit()
        
        logger.info(f"Conteo físico completado: {count.count_number}")
        return count
    
    # ==================== REPORTES ====================
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Obtener resumen del inventario"""
        total_products = self.db.query(Product).count()
        
        # Productos por estado de stock
        normal_stock = self.db.query(Product).filter(
            and_(
                Product.stock > func.coalesce(Product.min_stock, 0),
                Product.stock < func.coalesce(Product.max_stock, 999999)
            )
        ).count()
        
        low_stock = self.db.query(Product).filter(
            and_(
                Product.stock <= func.coalesce(Product.min_stock, 0),
                Product.stock > 0
            )
        ).count()
        
        out_of_stock = self.db.query(Product).filter(Product.stock == 0).count()
        
        overstock = self.db.query(Product).filter(
            Product.stock >= func.coalesce(Product.max_stock, 999999)
        ).count()
        
        # Valores totales
        total_value = self.db.query(func.sum(Product.stock * Product.price)).scalar() or 0
        total_cost = self.db.query(func.sum(Product.stock * func.coalesce(Product.cost_price, 0))).scalar() or 0
        average_cost = total_cost / total_products if total_products > 0 else 0
        
        return {
            "total_products": total_products,
            "normal_stock": normal_stock,
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "overstock": overstock,
            "total_value": float(total_value),
            "total_cost": float(total_cost),
            "average_cost": float(average_cost),
            "last_updated": datetime.now()
        }
    
    def get_movement_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Obtener reporte de movimientos"""
        movements = self.db.query(InventoryMovement).filter(
            and_(
                InventoryMovement.created_at >= start_date,
                InventoryMovement.created_at <= end_date
            )
        ).all()
        
        total_movements = len(movements)
        total_quantity_in = sum(m.quantity for m in movements if m.movement_type in [MovementType.ENTRADA, MovementType.DEVOLUCION])
        total_quantity_out = sum(m.quantity for m in movements if m.movement_type in [MovementType.SALIDA, MovementType.MERMA, MovementType.CADUCIDAD])
        
        movements_by_type = {}
        movements_by_reason = {}
        
        for movement in movements:
            movements_by_type[movement.movement_type.value] = movements_by_type.get(movement.movement_type.value, 0) + 1
            movements_by_reason[movement.reason.value] = movements_by_reason.get(movement.reason.value, 0) + 1
        
        return {
            "period": f"{start_date} - {end_date}",
            "total_movements": total_movements,
            "total_quantity_in": total_quantity_in,
            "total_quantity_out": total_quantity_out,
            "movements_by_type": movements_by_type,
            "movements_by_reason": movements_by_reason
        }
    
    # ==================== UTILIDADES ====================
    
    def _update_product_stock(self, product_id: int):
        """Actualizar stock total del producto basado en lotes"""
        total_stock = self.db.query(func.sum(InventoryLot.quantity)).filter(
            and_(
                InventoryLot.product_id == product_id,
                InventoryLot.is_active == True
            )
        ).scalar() or 0
        
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.stock = int(total_stock)
            self.db.commit()
    
    def search_inventory(self, filters: InventorySearchFilters) -> List[Dict[str, Any]]:
        """Búsqueda avanzada de inventario"""
        query = self.db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.subcategory),
            joinedload(Product.default_location)
        )
        
        # Aplicar filtros
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.code.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        if filters.category_id:
            query = query.filter(Product.category_id == filters.category_id)
        
        if filters.location_id:
            query = query.filter(Product.default_location_id == filters.location_id)
        
        if filters.stock_status:
            if filters.stock_status == "normal":
                query = query.filter(
                    and_(
                        Product.stock > func.coalesce(Product.min_stock, 0),
                        Product.stock < func.coalesce(Product.max_stock, 999999)
                    )
                )
            elif filters.stock_status == "low":
                query = query.filter(
                    and_(
                        Product.stock <= func.coalesce(Product.min_stock, 0),
                        Product.stock > 0
                    )
                )
            elif filters.stock_status == "out":
                query = query.filter(Product.stock == 0)
            elif filters.stock_status == "overstock":
                query = query.filter(Product.stock >= func.coalesce(Product.max_stock, 999999))
        
        if filters.track_lots is not None:
            query = query.filter(Product.track_lots == filters.track_lots)
        
        if filters.track_expiration is not None:
            query = query.filter(Product.track_expiration == filters.track_expiration)
        
        if not filters.include_inactive:
            query = query.filter(Product.is_active == True)
        
        products = query.offset(filters.offset).limit(filters.limit).all()
        
        # Formatear resultados
        results = []
        for product in products:
            product_data = {
                "id": product.id,
                "code": product.code,
                "name": product.name,
                "stock": product.stock,
                "min_stock": product.min_stock,
                "max_stock": product.max_stock,
                "price": float(product.price),
                "cost_price": float(product.cost_price) if product.cost_price else None,
                "stock_status": product.stock_status,
                "category_name": product.category.name if product.category else None,
                "location_name": product.default_location.name if product.default_location else None,
                "track_lots": product.track_lots,
                "track_expiration": product.track_expiration,
                "total_stock_value": float(product.total_stock_value),
                "needs_reorder": product.needs_reorder
            }
            results.append(product_data)
        
        return results
