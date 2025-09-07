"""
Router de inventario profesionalizado
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import logging

from app.database import get_db
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.product import Category
from app.models.inventory import (
    InventoryMovement, InventoryLot, InventoryLocation, 
    InventoryAlert, InventoryCount, InventoryCountItem,
    MovementType, MovementReason
)
from app.auth.dependencies import get_current_active_user
from app.services.inventory_service import InventoryService
from app.schemas.inventory import (
    InventoryMovementCreate, InventoryMovementResponse,
    InventoryLotCreate, InventoryLotResponse,
    InventoryLocationCreate, InventoryLocationResponse,
    InventoryAlertResponse, InventoryCountCreate, InventoryCountResponse,
    InventoryCountItemCreate, InventoryCountItemResponse,
    StockTransfer, BulkStockAdjustment, InventorySearchFilters,
    InventorySummaryResponse, InventoryReportFilters,
    InventoryMovementReport, LowStockReport, ExpirationReport
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/inventory", tags=["inventario"])


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """Dependency para obtener el servicio de inventario"""
    return InventoryService(db)


# ==================== ENDPOINTS DE UBICACIONES ====================

@router.post("/locations", response_model=InventoryLocationResponse)
def create_location(
    location_data: InventoryLocationCreate,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Crear nueva ubicación de inventario"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear ubicaciones"
        )
    
    try:
        location = inventory_service.create_location(location_data)
        return location
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/locations", response_model=List[InventoryLocationResponse])
def get_locations(
    active_only: bool = Query(True, description="Solo ubicaciones activas"),
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener ubicaciones de inventario"""
    locations = inventory_service.get_locations(active_only=active_only)
    return locations


@router.get("/locations/default", response_model=InventoryLocationResponse)
def get_default_location(
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener ubicación por defecto"""
    location = inventory_service.get_default_location()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay ubicación por defecto configurada"
        )
    return location


# ==================== ENDPOINTS DE LOTES ====================

@router.post("/lots", response_model=InventoryLotResponse)
def create_lot(
    lot_data: InventoryLotCreate,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Crear nuevo lote de inventario"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear lotes"
        )
    
    try:
        lot = inventory_service.create_lot(lot_data)
        return lot
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/lots/product/{product_id}", response_model=List[InventoryLotResponse])
def get_product_lots(
    product_id: int,
    active_only: bool = Query(True, description="Solo lotes activos"),
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener lotes de un producto"""
    lots = inventory_service.get_product_lots(product_id, active_only=active_only)
    return lots


@router.get("/lots/expiring", response_model=List[InventoryLotResponse])
def get_expiring_lots(
    days: int = Query(30, ge=1, le=365, description="Días hasta la expiración"),
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener lotes próximos a expirar"""
    lots = inventory_service.get_expiring_lots(days=days)
    return lots


@router.get("/lots/expired", response_model=List[InventoryLotResponse])
def get_expired_lots(
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener lotes expirados"""
    lots = inventory_service.get_expired_lots()
    return lots


# ==================== ENDPOINTS DE MOVIMIENTOS ====================

@router.post("/movements", response_model=InventoryMovementResponse)
def create_movement(
    movement_data: InventoryMovementCreate,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Crear movimiento de inventario"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR, UserRole.CAJA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear movimientos de inventario"
        )
    
    try:
        movement = inventory_service.create_movement(movement_data, current_user.id)
        return movement
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/movements/bulk", response_model=List[InventoryMovementResponse])
def bulk_adjustment(
    adjustments: BulkStockAdjustment,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Ajuste masivo de stock"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar ajustes masivos"
        )
    
    try:
        movements = inventory_service.bulk_adjustment(adjustments, current_user.id)
        return movements
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/transfer", response_model=Dict[str, Any])
def transfer_stock(
    transfer_data: StockTransfer,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Transferir stock entre ubicaciones"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para transferir stock"
        )
    
    try:
        exit_movement, entry_movement = inventory_service.transfer_stock(transfer_data, current_user.id)
        return {
            "message": "Transferencia completada exitosamente",
            "exit_movement_id": exit_movement.id,
            "entry_movement_id": entry_movement.id,
            "quantity": transfer_data.quantity
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/movements", response_model=List[InventoryMovementResponse])
def get_movements(
    product_id: Optional[int] = Query(None, description="Filtrar por producto"),
    movement_type: Optional[MovementType] = Query(None, description="Filtrar por tipo de movimiento"),
    start_date: Optional[date] = Query(None, description="Fecha de inicio"),
    end_date: Optional[date] = Query(None, description="Fecha de fin"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener movimientos de inventario con filtros"""
    filters = {}
    if product_id:
        filters['product_id'] = product_id
    if movement_type:
        filters['movement_type'] = movement_type
    if start_date:
        filters['start_date'] = start_date
    if end_date:
        filters['end_date'] = end_date
    
    movements = inventory_service.get_movements(filters=filters, limit=limit, offset=offset)
    return movements


@router.get("/movements/product/{product_id}", response_model=List[InventoryMovementResponse])
def get_product_movements(
    product_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener movimientos de un producto específico"""
    filters = {'product_id': product_id}
    movements = inventory_service.get_movements(filters=filters, limit=limit, offset=offset)
    return movements


# ==================== ENDPOINTS DE ALERTAS ====================

@router.get("/alerts", response_model=List[InventoryAlertResponse])
def get_alerts(
    alert_type: Optional[str] = Query(None, description="Filtrar por tipo de alerta"),
    active_only: bool = Query(True, description="Solo alertas activas"),
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener alertas de inventario"""
    if active_only:
        alerts = inventory_service.get_active_alerts(alert_type=alert_type)
    else:
        # Implementar para obtener todas las alertas
        alerts = []
    return alerts


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Reconocer alerta de inventario"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para reconocer alertas"
        )
    
    try:
        inventory_service.acknowledge_alert(alert_id, current_user.id)
        return {"message": "Alerta reconocida exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== ENDPOINTS DE CONTEOS FÍSICOS ====================

@router.post("/counts", response_model=InventoryCountResponse)
def create_count(
    count_data: InventoryCountCreate,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Crear conteo físico"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear conteos físicos"
        )
    
    try:
        count = inventory_service.create_count(count_data, current_user.id)
        return count
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/counts/{count_id}/items", response_model=InventoryCountItemResponse)
def add_count_item(
    count_id: int,
    item_data: InventoryCountItemCreate,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Agregar item a conteo físico"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para agregar items a conteos"
        )
    
    try:
        item_data.count_id = count_id
        item = inventory_service.add_count_item(item_data)
        return item
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/counts/{count_id}/complete", response_model=InventoryCountResponse)
def complete_count(
    count_id: int,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Completar conteo físico"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para completar conteos"
        )
    
    try:
        count = inventory_service.complete_count(count_id, current_user.id)
        return count
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== ENDPOINTS DE REPORTES ====================

@router.get("/summary", response_model=InventorySummaryResponse)
def get_inventory_summary(
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener resumen del inventario"""
    summary = inventory_service.get_inventory_summary()
    return summary


@router.get("/report/movements", response_model=InventoryMovementReport)
def get_movement_report(
    start_date: date = Query(..., description="Fecha de inicio"),
    end_date: date = Query(..., description="Fecha de fin"),
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener reporte de movimientos de inventario"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver reportes de movimientos"
        )
    
    report = inventory_service.get_movement_report(start_date, end_date)
    return report


@router.get("/report/low-stock", response_model=LowStockReport)
def get_low_stock_report(
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener reporte de productos con stock bajo"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver reportes de stock bajo"
        )
    
    # Obtener productos con stock bajo
    low_stock_products = inventory_service.db.query(Product).filter(
        and_(
            Product.stock <= func.coalesce(Product.min_stock, 0),
            Product.stock > 0
        )
    ).all()
    
    out_of_stock_products = inventory_service.db.query(Product).filter(Product.stock == 0).all()
    
    total_value_at_risk = sum(p.total_stock_value for p in low_stock_products + out_of_stock_products)
    
    return {
        "low_stock_count": len(low_stock_products),
        "out_of_stock_count": len(out_of_stock_products),
        "total_value_at_risk": float(total_value_at_risk),
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "current_stock": p.stock,
                "min_stock": p.min_stock,
                "category": p.category.name if p.category else None,
                "needed": p.min_stock - p.stock if p.min_stock else 0,
                "stock_value": float(p.total_stock_value)
            }
            for p in low_stock_products + out_of_stock_products
        ]
    }


@router.get("/report/expiration", response_model=ExpirationReport)
def get_expiration_report(
    days: int = Query(30, ge=1, le=365, description="Días hasta la expiración"),
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener reporte de productos próximos a expirar"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver reportes de expiración"
        )
    
    expiring_lots = inventory_service.get_expiring_lots(days=days)
    expired_lots = inventory_service.get_expired_lots()
    
    total_value_expiring = sum(
        lot.total_cost or 0 for lot in expiring_lots
    )
    total_value_expired = sum(
        lot.total_cost or 0 for lot in expired_lots
    )
    
    return {
        "expiring_soon_count": len(expiring_lots),
        "expired_count": len(expired_lots),
        "total_value_expiring": float(total_value_expiring),
        "total_value_expired": float(total_value_expired),
        "products": [
            {
                "id": lot.product.id,
                "name": lot.product.name,
                "lot_number": lot.lot_number,
                "expiration_date": lot.expiration_date,
                "days_until_expiry": lot.days_until_expiry,
                "quantity": lot.available_quantity,
                "value": float(lot.total_cost or 0)
            }
            for lot in expiring_lots + expired_lots
        ]
    }


# ==================== ENDPOINTS DE BÚSQUEDA ====================

@router.post("/search", response_model=List[Dict[str, Any]])
def search_inventory(
    filters: InventorySearchFilters,
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Búsqueda avanzada de inventario"""
    results = inventory_service.search_inventory(filters)
    return results


# ==================== ENDPOINTS LEGACY (COMPATIBILIDAD) ====================

@router.get("/low-stock")
def get_low_stock_products(
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener productos con stock bajo (endpoint legacy)"""
    products = inventory_service.db.query(Product).filter(
        and_(
            Product.stock <= func.coalesce(Product.min_stock, 0),
            Product.stock > 0
        )
    ).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "stock": p.stock,
            "min_stock": p.min_stock,
            "category_name": p.category.name if p.category else None,
            "price": float(p.price)
        }
        for p in products
    ]


@router.get("/out-of-stock")
def get_out_of_stock_products(
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener productos sin stock (endpoint legacy)"""
    products = inventory_service.db.query(Product).filter(Product.stock == 0).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "stock": p.stock,
            "min_stock": p.min_stock,
            "category_name": p.category.name if p.category else None,
            "price": float(p.price)
        }
        for p in products
    ]


@router.post("/adjust")
def adjust_stock_legacy(
    adjustment: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Ajustar stock (endpoint legacy)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR, UserRole.CAJA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ajustar stock"
        )
    
    try:
        # Convertir formato legacy a nuevo formato
        movement_data = InventoryMovementCreate(
            product_id=adjustment['product_id'],
            movement_type=MovementType.AJUSTE,
            reason=MovementReason.AJUSTE_POSITIVO if adjustment['adjustment_type'] == 'add' else MovementReason.AJUSTE_NEGATIVO,
            quantity=abs(adjustment['quantity']),
            notes=adjustment.get('notes', '')
        )
        
        movement = inventory_service.create_movement(movement_data, current_user.id)
        
        return {
            "message": "Stock ajustado correctamente",
            "movement_id": movement.id,
            "previous_stock": movement.previous_stock,
            "new_stock": movement.new_stock
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/report/daily")
def get_daily_inventory_report(
    report_date: date = Query(default_factory=date.today),
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Obtener reporte diario de inventario (endpoint legacy)"""
    movements = inventory_service.db.query(InventoryMovement).filter(
        func.date(InventoryMovement.created_at) == report_date
    ).all()
    
    summary = {
        "date": report_date,
        "total_movements": len(movements),
        "additions": len([m for m in movements if m.movement_type in [MovementType.ENTRADA, MovementType.DEVOLUCION]]),
        "subtractions": len([m for m in movements if m.movement_type in [MovementType.SALIDA, MovementType.MERMA, MovementType.CADUCIDAD]]),
        "total_added": sum([m.quantity for m in movements if m.movement_type in [MovementType.ENTRADA, MovementType.DEVOLUCION]]),
        "total_subtracted": sum([m.quantity for m in movements if m.movement_type in [MovementType.SALIDA, MovementType.MERMA, MovementType.CADUCIDAD]]),
        "movements": [
            {
                "id": m.id,
                "product_name": m.product.name,
                "type": m.movement_type.value,
                "quantity": m.quantity,
                "reason": m.reason.value,
                "created_at": m.created_at,
                "user": m.user.username if m.user else "Sistema"
            }
            for m in movements
        ]
    }
    
    return summary


# ==================== ENDPOINT PARA CARGA DE EXCEL ====================

@router.post("/upload-excel")
def upload_excel_inventory(
    upload_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Cargar inventario desde archivo Excel"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ALMACEN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cargar inventario desde Excel"
        )
    
    try:
        products_data = upload_data.get('products', [])
        options = upload_data.get('options', {})
        
        if not products_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontraron datos de productos en el archivo"
            )
        
        created_count = 0
        updated_count = 0
        categories_created = 0
        stock_movements_created = 0
        errors = []
        
        # Obtener ubicación por defecto
        default_location = inventory_service.get_default_location()
        if not default_location:
            # Crear ubicación por defecto si no existe
            default_location = inventory_service.create_location(
                InventoryLocationCreate(
                    name="Almacén Principal",
                    description="Ubicación principal del almacén",
                    is_default=True
                )
            )
        
        for i, product_data in enumerate(products_data):
            try:
                # Validar datos obligatorios
                required_fields = ['nombre', 'precio', 'categoria_id', 'stock_actual', 'precio_compra']
                for field in required_fields:
                    if field not in product_data or product_data[field] is None:
                        errors.append(f"Fila {i+2}: Campo '{field}' es obligatorio")
                        continue
                
                # Buscar o crear categoría
                category_id = int(product_data['categoria_id'])
                category = inventory_service.db.query(Category).filter(Category.id == category_id).first()
                
                if not category and options.get('create_missing_categories', False):
                    # Crear categoría automáticamente
                    category = Category(
                        name=f"Categoría {category_id}",
                        description=f"Categoría creada automáticamente desde Excel"
                    )
                    inventory_service.db.add(category)
                    inventory_service.db.commit()
                    inventory_service.db.refresh(category)
                    categories_created += 1
                elif not category:
                    errors.append(f"Fila {i+2}: Categoría con ID {category_id} no existe")
                    continue
                
                # Buscar producto existente por nombre
                existing_product = inventory_service.db.query(Product).filter(
                    func.lower(Product.name) == func.lower(product_data['nombre'])
                ).first()
                
                if existing_product and options.get('update_existing_products', False):
                    # Actualizar producto existente
                    existing_product.price = float(product_data['precio'])
                    existing_product.description = product_data.get('descripcion', existing_product.description)
                    existing_product.category_id = category.id
                    
                    # Actualizar campos de inventario si existen
                    if 'punto_reorden' in product_data:
                        existing_product.reorder_point = int(product_data['punto_reorden'])
                    if 'cantidad_reorden' in product_data:
                        existing_product.reorder_quantity = int(product_data['cantidad_reorden'])
                    if 'unidad_medida' in product_data:
                        existing_product.unit_of_measure = product_data['unidad_medida']
                    if 'peso' in product_data:
                        existing_product.weight = float(product_data['peso'])
                    if 'dimensiones' in product_data:
                        existing_product.dimensions = product_data['dimensiones']
                    if 'codigo_barras' in product_data:
                        existing_product.barcode = product_data['codigo_barras']
                    if 'sku' in product_data:
                        existing_product.sku = product_data['sku']
                    
                    inventory_service.db.commit()
                    updated_count += 1
                    
                else:
                    # Crear nuevo producto
                    new_product = Product(
                        name=product_data['nombre'],
                        price=float(product_data['precio']),
                        description=product_data.get('descripcion', ''),
                        category_id=category.id,
                        stock=0,  # Se establecerá con el movimiento de stock
                        min_stock=product_data.get('punto_reorden', 0),
                        reorder_point=product_data.get('punto_reorden', 0),
                        reorder_quantity=product_data.get('cantidad_reorden', 0),
                        unit_of_measure=product_data.get('unidad_medida', 'unidades'),
                        weight=product_data.get('peso'),
                        dimensions=product_data.get('dimensiones'),
                        barcode=product_data.get('codigo_barras'),
                        sku=product_data.get('sku'),
                        default_location_id=default_location.id
                    )
                    
                    inventory_service.db.add(new_product)
                    inventory_service.db.commit()
                    inventory_service.db.refresh(new_product)
                    created_count += 1
                    
                    # Crear movimiento de stock inicial si se solicita
                    if options.get('create_initial_stock', False) and product_data['stock_actual'] > 0:
                        try:
                            movement_data = InventoryMovementCreate(
                                product_id=new_product.id,
                                movement_type=MovementType.ENTRADA,
                                reason=MovementReason.COMPRA,
                                quantity=int(product_data['stock_actual']),
                                unit_cost=float(product_data['precio_compra']),
                                notes=f"Stock inicial cargado desde Excel - Precio compra: ${product_data['precio_compra']}"
                            )
                            
                            inventory_service.create_movement(movement_data, current_user.id)
                            stock_movements_created += 1
                            
                        except Exception as e:
                            errors.append(f"Fila {i+2}: Error al crear movimiento de stock: {str(e)}")
                
            except Exception as e:
                errors.append(f"Fila {i+2}: Error procesando producto: {str(e)}")
                continue
        
        return {
            "message": "Carga de inventario completada",
            "created_count": created_count,
            "updated_count": updated_count,
            "categories_created": categories_created,
            "stock_movements_created": stock_movements_created,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Error en carga de Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
