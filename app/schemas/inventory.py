"""
Esquemas Pydantic para el módulo de inventario profesionalizado
"""
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class MovementTypeEnum(str, Enum):
    """Tipos de movimiento de inventario"""
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"
    TRANSFERENCIA = "transferencia"
    DEVOLUCION = "devolucion"
    MERMA = "merma"
    CADUCIDAD = "caducidad"
    INVENTARIO_FISICO = "inventario_fisico"


class MovementReasonEnum(str, Enum):
    """Razones específicas para movimientos de inventario"""
    # Entradas
    COMPRA_PROVEEDOR = "compra_proveedor"
    DEVOLUCION_CLIENTE = "devolucion_cliente"
    TRANSFERENCIA_ENTRADA = "transferencia_entrada"
    AJUSTE_POSITIVO = "ajuste_positivo"
    
    # Salidas
    VENTA = "venta"
    MERMA_NATURAL = "merma_natural"
    CADUCIDAD = "caducidad"
    TRANSFERENCIA_SALIDA = "transferencia_salida"
    AJUSTE_NEGATIVO = "ajuste_negativo"
    ROBOTES = "robotes"
    MUESTRAS = "muestras"


class AlertLevelEnum(str, Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class CountStatusEnum(str, Enum):
    """Estados de conteo físico"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Esquemas base
class InventoryLocationBase(BaseModel):
    """Esquema base para ubicaciones de inventario"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la ubicación")
    description: Optional[str] = Field(None, max_length=500, description="Descripción de la ubicación")
    is_default: bool = Field(False, description="Si es la ubicación por defecto")


class InventoryLocationCreate(InventoryLocationBase):
    """Esquema para crear ubicación de inventario"""
    pass


class InventoryLocationUpdate(BaseModel):
    """Esquema para actualizar ubicación de inventario"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class InventoryLocationResponse(InventoryLocationBase):
    """Esquema de respuesta para ubicación de inventario"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Esquemas para lotes
class InventoryLotBase(BaseModel):
    """Esquema base para lotes de inventario"""
    lot_number: str = Field(..., min_length=1, max_length=50, description="Número de lote")
    batch_number: Optional[str] = Field(None, max_length=50, description="Número de lote del proveedor")
    supplier_lot: Optional[str] = Field(None, max_length=50, description="Lote del proveedor")
    quantity: int = Field(..., ge=0, description="Cantidad en el lote")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Costo unitario")
    manufacturing_date: Optional[date] = Field(None, description="Fecha de fabricación")
    expiration_date: Optional[date] = Field(None, description="Fecha de expiración")
    best_before_date: Optional[date] = Field(None, description="Fecha de consumo preferente")
    purchase_order: Optional[str] = Field(None, max_length=50, description="Orden de compra")
    invoice_number: Optional[str] = Field(None, max_length=50, description="Número de factura")


class InventoryLotCreate(InventoryLotBase):
    """Esquema para crear lote de inventario"""
    product_id: int = Field(..., gt=0, description="ID del producto")
    location_id: int = Field(..., gt=0, description="ID de la ubicación")
    supplier_id: Optional[int] = Field(None, gt=0, description="ID del proveedor")
    
    @validator('expiration_date')
    def validate_expiration_date(cls, v, values):
        if v and 'manufacturing_date' in values and values['manufacturing_date']:
            if v <= values['manufacturing_date']:
                raise ValueError("La fecha de expiración debe ser posterior a la fecha de fabricación")
        return v
    
    @validator('best_before_date')
    def validate_best_before_date(cls, v, values):
        if v and 'expiration_date' in values and values['expiration_date']:
            if v >= values['expiration_date']:
                raise ValueError("La fecha de consumo preferente debe ser anterior a la fecha de expiración")
        return v


class InventoryLotUpdate(BaseModel):
    """Esquema para actualizar lote de inventario"""
    quantity: Optional[int] = Field(None, ge=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    expiration_date: Optional[date] = None
    is_active: Optional[bool] = None


class InventoryLotResponse(InventoryLotBase):
    """Esquema de respuesta para lote de inventario"""
    id: int
    product_id: int
    location_id: int
    supplier_id: Optional[int] = None
    reserved_quantity: int
    available_quantity: int
    total_cost: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Propiedades calculadas
    is_expired: bool
    is_expiring_soon: bool
    days_until_expiry: Optional[int] = None
    
    class Config:
        from_attributes = True


# Esquemas para movimientos
class InventoryMovementBase(BaseModel):
    """Esquema base para movimientos de inventario"""
    movement_type: MovementTypeEnum = Field(..., description="Tipo de movimiento")
    reason: MovementReasonEnum = Field(..., description="Razón del movimiento")
    reason_detail: Optional[str] = Field(None, max_length=200, description="Detalle adicional de la razón")
    quantity: int = Field(..., description="Cantidad del movimiento")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Costo unitario")
    reference_type: Optional[str] = Field(None, max_length=50, description="Tipo de referencia")
    reference_id: Optional[int] = Field(None, description="ID de referencia")
    reference_number: Optional[str] = Field(None, max_length=50, description="Número de referencia")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")
    tags: Optional[str] = Field(None, max_length=200, description="Etiquetas para categorización")


class InventoryMovementCreate(InventoryMovementBase):
    """Esquema para crear movimiento de inventario"""
    product_id: int = Field(..., gt=0, description="ID del producto")
    lot_id: Optional[int] = Field(None, gt=0, description="ID del lote (opcional)")
    location_id: Optional[int] = Field(None, gt=0, description="ID de la ubicación")
    
    @validator('quantity')
    def validate_quantity(cls, v, values):
        if 'movement_type' in values:
            if values['movement_type'] in [MovementTypeEnum.SALIDA, MovementTypeEnum.MERMA, MovementTypeEnum.CADUCIDAD]:
                if v <= 0:
                    raise ValueError("La cantidad debe ser positiva para salidas")
        return v


class InventoryMovementResponse(InventoryMovementBase):
    """Esquema de respuesta para movimiento de inventario"""
    id: int
    product_id: int
    lot_id: Optional[int] = None
    location_id: Optional[int] = None
    user_id: int
    previous_stock: int
    new_stock: int
    total_cost: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Información relacionada
    product_name: Optional[str] = None
    lot_number: Optional[str] = None
    location_name: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Esquemas para alertas
class InventoryAlertBase(BaseModel):
    """Esquema base para alertas de inventario"""
    alert_type: str = Field(..., max_length=50, description="Tipo de alerta")
    alert_level: AlertLevelEnum = Field(..., description="Nivel de alerta")
    message: str = Field(..., max_length=1000, description="Mensaje de la alerta")


class InventoryAlertCreate(InventoryAlertBase):
    """Esquema para crear alerta de inventario"""
    product_id: int = Field(..., gt=0, description="ID del producto")
    lot_id: Optional[int] = Field(None, gt=0, description="ID del lote (opcional)")


class InventoryAlertUpdate(BaseModel):
    """Esquema para actualizar alerta de inventario"""
    is_active: Optional[bool] = None
    is_acknowledged: Optional[bool] = None


class InventoryAlertResponse(InventoryAlertBase):
    """Esquema de respuesta para alerta de inventario"""
    id: int
    product_id: int
    lot_id: Optional[int] = None
    is_active: bool
    is_acknowledged: bool
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    
    # Información relacionada
    product_name: Optional[str] = None
    lot_number: Optional[str] = None
    acknowledged_user_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Esquemas para conteos físicos
class InventoryCountBase(BaseModel):
    """Esquema base para conteos físicos"""
    count_number: str = Field(..., min_length=1, max_length=50, description="Número de conteo")
    count_date: date = Field(..., description="Fecha del conteo")
    location_id: Optional[int] = Field(None, gt=0, description="ID de la ubicación")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas del conteo")


class InventoryCountCreate(InventoryCountBase):
    """Esquema para crear conteo físico"""
    pass


class InventoryCountUpdate(BaseModel):
    """Esquema para actualizar conteo físico"""
    status: Optional[CountStatusEnum] = None
    notes: Optional[str] = Field(None, max_length=1000)
    completed_at: Optional[datetime] = None


class InventoryCountResponse(InventoryCountBase):
    """Esquema de respuesta para conteo físico"""
    id: int
    status: CountStatusEnum
    created_by: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # Información relacionada
    location_name: Optional[str] = None
    created_user_name: Optional[str] = None
    total_items: int = 0
    completed_items: int = 0
    
    class Config:
        from_attributes = True


# Esquemas para items de conteo
class InventoryCountItemBase(BaseModel):
    """Esquema base para items de conteo"""
    expected_quantity: int = Field(..., ge=0, description="Cantidad esperada")
    actual_quantity: Optional[int] = Field(None, ge=0, description="Cantidad real")
    notes: Optional[str] = Field(None, max_length=500, description="Notas del item")


class InventoryCountItemCreate(InventoryCountItemBase):
    """Esquema para crear item de conteo"""
    count_id: int = Field(..., gt=0, description="ID del conteo")
    product_id: int = Field(..., gt=0, description="ID del producto")
    lot_id: Optional[int] = Field(None, gt=0, description="ID del lote (opcional)")


class InventoryCountItemUpdate(BaseModel):
    """Esquema para actualizar item de conteo"""
    actual_quantity: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class InventoryCountItemResponse(InventoryCountItemBase):
    """Esquema de respuesta para item de conteo"""
    id: int
    count_id: int
    product_id: int
    lot_id: Optional[int] = None
    variance: Optional[int] = None
    variance_percentage: Optional[float] = None
    
    # Información relacionada
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    lot_number: Optional[str] = None
    
    class Config:
        from_attributes = True


# Esquemas para reportes
class InventorySummaryResponse(BaseModel):
    """Esquema de respuesta para resumen de inventario"""
    total_products: int
    normal_stock: int
    low_stock: int
    out_of_stock: int
    overstock: int
    total_value: Decimal
    total_cost: Decimal
    average_cost: Decimal
    last_updated: datetime


class InventoryReportFilters(BaseModel):
    """Esquema para filtros de reportes de inventario"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location_id: Optional[int] = None
    category_id: Optional[int] = None
    movement_type: Optional[MovementTypeEnum] = None
    reason: Optional[MovementReasonEnum] = None
    product_id: Optional[int] = None
    include_expired: bool = False
    include_expiring_soon: bool = True


class InventoryMovementReport(BaseModel):
    """Esquema para reporte de movimientos de inventario"""
    period: str
    total_movements: int
    total_quantity_in: int
    total_quantity_out: int
    total_value_in: Decimal
    total_value_out: Decimal
    movements_by_type: Dict[str, int]
    movements_by_reason: Dict[str, int]
    top_products: List[Dict[str, Any]]


class LowStockReport(BaseModel):
    """Esquema para reporte de stock bajo"""
    low_stock_count: int
    out_of_stock_count: int
    total_value_at_risk: Decimal
    products: List[Dict[str, Any]]


class ExpirationReport(BaseModel):
    """Esquema para reporte de productos próximos a expirar"""
    expiring_soon_count: int
    expired_count: int
    total_value_expiring: Decimal
    total_value_expired: Decimal
    products: List[Dict[str, Any]]


# Esquemas para operaciones especiales
class BulkStockAdjustment(BaseModel):
    """Esquema para ajuste masivo de stock"""
    adjustments: List[InventoryMovementCreate] = Field(..., min_items=1, max_items=100)
    
    @validator('adjustments')
    def validate_adjustments(cls, v):
        if not v:
            raise ValueError("Debe incluir al menos un ajuste")
        return v


class StockTransfer(BaseModel):
    """Esquema para transferencia de stock entre ubicaciones"""
    product_id: int = Field(..., gt=0)
    lot_id: Optional[int] = Field(None, gt=0)
    quantity: int = Field(..., gt=0)
    from_location_id: int = Field(..., gt=0)
    to_location_id: int = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('to_location_id')
    def validate_different_locations(cls, v, values):
        if 'from_location_id' in values and v == values['from_location_id']:
            raise ValueError("Las ubicaciones de origen y destino deben ser diferentes")
        return v


class InventorySearchFilters(BaseModel):
    """Esquema para filtros de búsqueda de inventario"""
    search: Optional[str] = None
    category_id: Optional[int] = None
    location_id: Optional[int] = None
    stock_status: Optional[str] = None  # normal, low, out, overstock
    track_lots: Optional[bool] = None
    track_expiration: Optional[bool] = None
    include_inactive: bool = False
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
