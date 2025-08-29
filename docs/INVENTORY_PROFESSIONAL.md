# 📦 Módulo de Inventario Profesionalizado

## 🎯 Descripción General

El módulo de inventario ha sido completamente rediseñado y profesionalizado para ofrecer un control de inventario de nivel empresarial con las siguientes características:

- **Trazabilidad completa** por lotes y ubicaciones
- **Control de caducidad** automático
- **Alertas inteligentes** en tiempo real
- **Conteos físicos** automatizados
- **Reportes avanzados** y analytics
- **Transferencias** entre ubicaciones
- **Gestión de costos** detallada

## 🏗️ Arquitectura del Sistema

### Modelos de Datos

#### 1. **InventoryLocation** - Ubicaciones de Inventario
```python
class InventoryLocation(Base):
    name: str                    # Nombre de la ubicación
    description: str             # Descripción
    is_active: bool              # Estado activo/inactivo
    is_default: bool             # Ubicación por defecto
```

#### 2. **InventoryLot** - Lotes de Inventario
```python
class InventoryLot(Base):
    product_id: int              # Producto asociado
    location_id: int             # Ubicación del lote
    lot_number: str              # Número de lote
    quantity: int                # Cantidad total
    available_quantity: int      # Cantidad disponible
    reserved_quantity: int       # Cantidad reservada
    unit_cost: Decimal           # Costo unitario
    expiration_date: date        # Fecha de expiración
    manufacturing_date: date     # Fecha de fabricación
```

#### 3. **InventoryMovement** - Movimientos de Inventario
```python
class InventoryMovement(Base):
    product_id: int              # Producto
    lot_id: int                  # Lote (opcional)
    location_id: int             # Ubicación
    movement_type: MovementType  # Tipo de movimiento
    reason: MovementReason       # Razón del movimiento
    quantity: int                # Cantidad
    unit_cost: Decimal           # Costo unitario
    previous_stock: int          # Stock anterior
    new_stock: int               # Stock nuevo
```

#### 4. **InventoryAlert** - Alertas de Inventario
```python
class InventoryAlert(Base):
    product_id: int              # Producto
    lot_id: int                  # Lote (opcional)
    alert_type: str              # Tipo de alerta
    alert_level: str             # Nivel (info/warning/critical)
    message: str                 # Mensaje de la alerta
    is_acknowledged: bool        # Si fue reconocida
```

#### 5. **InventoryCount** - Conteos Físicos
```python
class InventoryCount(Base):
    count_number: str            # Número de conteo
    count_date: date             # Fecha del conteo
    location_id: int             # Ubicación
    status: str                  # Estado del conteo
    created_by: int              # Usuario que lo creó
```

## 🔧 Funcionalidades Principales

### 1. **Gestión de Ubicaciones**

#### Crear Ubicación
```bash
POST /api/v1/inventory/locations
{
    "name": "Almacén Principal",
    "description": "Ubicación principal del almacén",
    "is_default": true
}
```

#### Listar Ubicaciones
```bash
GET /api/v1/inventory/locations?active_only=true
```

### 2. **Gestión de Lotes**

#### Crear Lote
```bash
POST /api/v1/inventory/lots
{
    "product_id": 1,
    "location_id": 1,
    "lot_number": "LOT-2024-001",
    "quantity": 100,
    "unit_cost": 15.50,
    "expiration_date": "2024-12-31",
    "manufacturing_date": "2024-01-15"
}
```

#### Obtener Lotes de Producto
```bash
GET /api/v1/inventory/lots/product/1?active_only=true
```

#### Lotes Próximos a Expirar
```bash
GET /api/v1/inventory/lots/expiring?days=30
```

### 3. **Movimientos de Inventario**

#### Crear Movimiento
```bash
POST /api/v1/inventory/movements
{
    "product_id": 1,
    "lot_id": 1,
    "location_id": 1,
    "movement_type": "entrada",
    "reason": "compra_proveedor",
    "quantity": 50,
    "unit_cost": 15.50,
    "notes": "Compra de proveedor ABC"
}
```

#### Ajuste Masivo
```bash
POST /api/v1/inventory/movements/bulk
{
    "adjustments": [
        {
            "product_id": 1,
            "movement_type": "entrada",
            "reason": "ajuste_positivo",
            "quantity": 10
        },
        {
            "product_id": 2,
            "movement_type": "salida",
            "reason": "merma_natural",
            "quantity": 5
        }
    ]
}
```

#### Transferencia entre Ubicaciones
```bash
POST /api/v1/inventory/transfer
{
    "product_id": 1,
    "lot_id": 1,
    "quantity": 20,
    "from_location_id": 1,
    "to_location_id": 2,
    "notes": "Transferencia a sucursal"
}
```

### 4. **Alertas Automáticas**

#### Obtener Alertas Activas
```bash
GET /api/v1/inventory/alerts?alert_type=low_stock&active_only=true
```

#### Reconocer Alerta
```bash
POST /api/v1/inventory/alerts/1/acknowledge
```

### 5. **Conteos Físicos**

#### Crear Conteo
```bash
POST /api/v1/inventory/counts
{
    "count_number": "COUNT-2024-001",
    "count_date": "2024-01-15",
    "location_id": 1,
    "notes": "Conteo mensual"
}
```

#### Agregar Item al Conteo
```bash
POST /api/v1/inventory/counts/1/items
{
    "product_id": 1,
    "lot_id": 1,
    "expected_quantity": 100
}
```

#### Completar Conteo
```bash
POST /api/v1/inventory/counts/1/complete
```

### 6. **Reportes Avanzados**

#### Resumen de Inventario
```bash
GET /api/v1/inventory/summary
```

#### Reporte de Movimientos
```bash
GET /api/v1/inventory/report/movements?start_date=2024-01-01&end_date=2024-01-31
```

#### Reporte de Stock Bajo
```bash
GET /api/v1/inventory/report/low-stock
```

#### Reporte de Expiración
```bash
GET /api/v1/inventory/report/expiration?days=30
```

### 7. **Búsqueda Avanzada**

```bash
POST /api/v1/inventory/search
{
    "search": "producto",
    "category_id": 1,
    "location_id": 1,
    "stock_status": "low",
    "track_lots": true,
    "limit": 50,
    "offset": 0
}
```

## 🎨 Tipos de Movimientos

### MovementType
- `entrada` - Entrada de mercancía
- `salida` - Salida de mercancía
- `ajuste` - Ajuste de inventario
- `transferencia` - Transferencia entre ubicaciones
- `devolucion` - Devolución de cliente
- `merma` - Pérdida por merma
- `caducidad` - Pérdida por caducidad
- `inventario_fisico` - Ajuste por conteo físico

### MovementReason
#### Entradas
- `compra_proveedor` - Compra de proveedor
- `devolucion_cliente` - Devolución de cliente
- `transferencia_entrada` - Transferencia de entrada
- `ajuste_positivo` - Ajuste positivo

#### Salidas
- `venta` - Venta
- `merma_natural` - Merma natural
- `caducidad` - Caducidad
- `transferencia_salida` - Transferencia de salida
- `ajuste_negativo` - Ajuste negativo
- `robotes` - Robotes
- `muestras` - Muestras

## 🔔 Sistema de Alertas

### Tipos de Alertas
- `low_stock` - Stock bajo
- `out_of_stock` - Sin stock
- `overstock` - Sobrestock
- `expiring_soon` - Próximo a expirar
- `expired` - Expirado

### Niveles de Alerta
- `info` - Informativo
- `warning` - Advertencia
- `critical` - Crítico

## 📊 Reportes Disponibles

### 1. **Resumen de Inventario**
- Total de productos
- Productos por estado de stock
- Valor total del inventario
- Costo promedio

### 2. **Reporte de Movimientos**
- Movimientos por período
- Cantidades de entrada/salida
- Análisis por tipo y razón
- Productos más movidos

### 3. **Reporte de Stock Bajo**
- Productos con stock bajo
- Productos sin stock
- Valor en riesgo
- Cantidad necesaria

### 4. **Reporte de Expiración**
- Lotes próximos a expirar
- Lotes expirados
- Valor de productos expirando
- Días hasta expiración

## 🔐 Control de Accesos

### Roles con Permisos de Inventario

#### **ADMIN** - Acceso completo
- Todas las funcionalidades
- Configuración del sistema
- Reportes avanzados

#### **ALMACEN** - Gestión de inventario
- Crear/editar ubicaciones
- Crear/editar lotes
- Movimientos de inventario
- Conteos físicos
- Alertas

#### **SUPERVISOR** - Supervisión
- Ver todos los reportes
- Aprobar movimientos
- Reconocer alertas
- Conteos físicos

#### **CAJA** - Operaciones básicas
- Movimientos de venta
- Ajustes básicos
- Ver alertas

#### **MESERO/COCINA** - Solo lectura
- Ver stock disponible
- Ver alertas básicas

## 🚀 Migración desde Versión Anterior

### 1. **Ejecutar Script de Migración**
```bash
python migrations/inventory_upgrade.py
```

### 2. **Verificar Migración**
```bash
# Verificar nuevas tablas
\dt inventory_*

# Verificar nuevas columnas en products
\d products

# Verificar nuevas columnas en inventory_movements
\d inventory_movements
```

### 3. **Configurar Ubicación por Defecto**
El script crea automáticamente una ubicación por defecto llamada "Almacén Principal".

### 4. **Migrar Datos Existentes**
Los datos existentes se migran automáticamente al nuevo formato.

## 📈 Optimizaciones de Rendimiento

### Índices Creados
- `idx_movement_product_date` - Movimientos por producto y fecha
- `idx_movement_type_date` - Movimientos por tipo y fecha
- `idx_movement_reference` - Movimientos por referencia
- `idx_movement_user_date` - Movimientos por usuario y fecha
- `idx_lot_product_location` - Lotes por producto y ubicación
- `idx_lot_expiration` - Lotes por fecha de expiración
- `idx_lot_number` - Lotes por número

### Consultas Optimizadas
- Búsqueda por lotes con expiración
- Movimientos con joins optimizados
- Reportes con agregaciones eficientes

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Configuración de alertas
INVENTORY_ALERT_DAYS=30          # Días para alerta de expiración
INVENTORY_LOW_STOCK_THRESHOLD=0.2 # Umbral para stock bajo (%)

# Configuración de reportes
INVENTORY_REPORT_LIMIT=1000      # Límite de registros en reportes
INVENTORY_CACHE_TTL=300          # TTL del cache en segundos
```

### Configuración de Productos
```python
# Configurar producto para trazabilidad
product.track_lots = True
product.track_expiration = True
product.shelf_life_days = 365
product.reorder_point = 10
product.reorder_quantity = 50
product.default_location_id = 1
```

## 🧪 Testing

### Tests Unitarios
```bash
# Ejecutar tests de inventario
pytest tests/test_inventory.py -v

# Tests específicos
pytest tests/test_inventory.py::test_create_movement -v
pytest tests/test_inventory.py::test_transfer_stock -v
pytest tests/test_inventory.py::test_alerts -v
```

### Tests de Integración
```bash
# Tests de API
pytest tests/test_inventory_api.py -v

# Tests de base de datos
pytest tests/test_inventory_db.py -v
```

## 📝 Logs y Monitoreo

### Logs del Sistema
```python
import logging

logger = logging.getLogger(__name__)

# Log de movimientos
logger.info(f"Movimiento creado: {movement.movement_type} - {movement.quantity} unidades")

# Log de alertas
logger.warning(f"Alerta de stock bajo: {product.name}")

# Log de errores
logger.error(f"Error en transferencia: {str(e)}")
```

### Métricas de Monitoreo
- Movimientos por hora
- Alertas activas
- Productos con stock bajo
- Lotes próximos a expirar
- Tiempo de respuesta de consultas

## 🔄 Mantenimiento

### Tareas Programadas
```bash
# Limpiar alertas antiguas (diario)
python scripts/clean_old_alerts.py

# Actualizar stock basado en lotes (cada hora)
python scripts/update_stock_from_lots.py

# Generar reportes automáticos (semanal)
python scripts/generate_inventory_reports.py
```

### Backup de Datos
```bash
# Backup de tablas de inventario
pg_dump -t inventory_* -t products sistema_pos > inventory_backup.sql

# Restaurar backup
psql sistema_pos < inventory_backup.sql
```

## 🆘 Solución de Problemas

### Problemas Comunes

#### 1. **Error de Stock Negativo**
```python
# Verificar stock antes de movimiento
if new_stock < 0:
    raise ValueError("Stock insuficiente para realizar el movimiento")
```

#### 2. **Lotes Duplicados**
```python
# Verificar unicidad de lotes
existing_lot = db.query(InventoryLot).filter(
    and_(
        InventoryLot.product_id == lot_data.product_id,
        InventoryLot.lot_number == lot_data.lot_number
    )
).first()
```

#### 3. **Alertas No Generadas**
```python
# Verificar configuración de productos
if product.min_stock is None:
    product.min_stock = 0
```

### Debugging
```python
# Habilitar logs detallados
logging.getLogger('app.services.inventory_service').setLevel(logging.DEBUG)

# Verificar estado de la base de datos
python scripts/check_inventory_integrity.py
```

## 📞 Soporte

Para problemas con el módulo de inventario:

1. **Revisar logs** en `/var/log/app/inventory.log`
2. **Verificar configuración** de productos y ubicaciones
3. **Ejecutar diagnóstico** con `python scripts/inventory_diagnostic.py`
4. **Contactar soporte** con logs y detalles del problema

---

## 🎉 Beneficios de la Versión Profesionalizada

### ✅ **Trazabilidad Completa**
- Seguimiento de lotes desde origen hasta destino
- Historial completo de movimientos
- Control de caducidad automático

### ✅ **Control de Costos**
- Costos por lote
- Valorización de inventario
- Análisis de rentabilidad

### ✅ **Alertas Inteligentes**
- Notificaciones automáticas
- Diferentes niveles de urgencia
- Reconocimiento de alertas

### ✅ **Reportes Avanzados**
- Analytics en tiempo real
- Exportación de datos
- Gráficos y métricas

### ✅ **Escalabilidad**
- Optimización de consultas
- Índices de rendimiento
- Arquitectura modular

### ✅ **Seguridad**
- Control de accesos por roles
- Auditoría completa
- Validaciones robustas
