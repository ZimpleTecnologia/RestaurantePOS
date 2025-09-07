# Sistema de Inventario Mejorado - Restaurante POS

## 📋 Resumen de Mejoras

Se ha actualizado el sistema de inventario del restaurante POS para manejar dos tipos de productos de manera separada y eficiente:

### 🏷️ Tipos de Productos

1. **Productos de Inventario (Materias Primas)**
   - Arroz 10KG
   - Pollo 40 porciones
   - Carne 50 porciones
   - Costilla Cerdo 2KG
   - etc.

2. **Productos de Venta (Platos Preparados)**
   - Costilla en salsa BBQ
   - Pollo a la plancha
   - etc.

## 🔧 Características Implementadas

### ✅ Gestión de Materias Primas
- **Stock tracking**: Control automático de inventario
- **Precio de compra**: Registro del costo de adquisición
- **Stock mínimo**: Alertas cuando el stock está bajo
- **Proveedores**: Asociación con proveedores
- **Unidades de medida**: KG, porciones, litros, etc.

### ✅ Gestión de Productos de Venta
- **Recetas**: Definición de ingredientes necesarios
- **Consumo automático**: Descuento de stock al vender
- **Cálculo de costos**: Costo total basado en ingredientes
- **Tiempo de preparación**: Control de tiempos de cocina

### ✅ Sistema de Recetas
- **Ingredientes**: Lista de materias primas necesarias
- **Cantidades**: Especificación exacta por ingrediente
- **Costos**: Cálculo automático del costo de producción
- **Instrucciones**: Pasos de preparación

### ✅ Consumo Automático de Inventario
- **Verificación de stock**: Antes de permitir la venta
- **Descuento automático**: Al confirmar la venta
- **Trazabilidad**: Registro de todos los movimientos
- **Alertas**: Notificaciones de stock insuficiente

## 🚀 Nuevos Endpoints API

### Productos
```
GET    /api/v1/products/inventory          # Productos de inventario
GET    /api/v1/products/sales              # Productos de venta
GET    /api/v1/products/inventory/low-stock # Stock bajo
GET    /api/v1/products/inventory/statistics # Estadísticas inventario
GET    /api/v1/products/sales/statistics   # Estadísticas ventas
```

### Recetas
```
POST   /api/v1/recipes/                    # Crear receta
GET    /api/v1/recipes/                    # Listar recetas
GET    /api/v1/recipes/{id}                # Obtener receta
PUT    /api/v1/recipes/{id}                # Actualizar receta
DELETE /api/v1/recipes/{id}                # Eliminar receta

POST   /api/v1/recipes/{id}/items          # Agregar ingrediente
PUT    /api/v1/recipes/items/{id}          # Actualizar ingrediente
DELETE /api/v1/recipes/items/{id}          # Eliminar ingrediente

GET    /api/v1/recipes/{id}/cost           # Calcular costo
POST   /api/v1/recipes/check-availability  # Verificar disponibilidad
POST   /api/v1/recipes/consume-inventory   # Consumir inventario
```

## 📊 Modelos de Datos

### Product
```python
class Product:
    id: int
    name: str
    product_type: ProductType  # INVENTORY | SALES
    price: Decimal
    purchase_price: Decimal    # Para materias primas
    stock_quantity: int
    min_stock_level: int
    supplier_id: int
    # ... otros campos
```

### Recipe
```python
class Recipe:
    id: int
    name: str
    product_id: int           # Producto de venta
    preparation_time: int
    total_cost: Decimal       # Calculado automáticamente
    # ... otros campos
```

### RecipeItem
```python
class RecipeItem:
    id: int
    recipe_id: int
    product_id: int           # Materia prima
    quantity: float
    unit: str
    unit_cost: Decimal        # Costo del ingrediente
    total_cost: Decimal       # quantity * unit_cost
```

## 🔄 Flujo de Trabajo

### 1. Configuración Inicial
1. **Crear materias primas** con stock, precio de compra y stock mínimo
2. **Crear productos de venta** (platos del menú)
3. **Definir recetas** asociando ingredientes a cada plato

### 2. Operación Diaria
1. **Venta de producto** → Sistema verifica disponibilidad de ingredientes
2. **Si hay stock** → Descuenta automáticamente las materias primas
3. **Si no hay stock** → Muestra alerta y no permite la venta

### 3. Gestión de Inventario
1. **Alertas automáticas** cuando el stock está bajo
2. **Reportes de consumo** por producto vendido
3. **Cálculo de costos** actualizado en tiempo real

## 🛠️ Instalación y Migración

### 1. Ejecutar Migración
```bash
python migrate_inventory_system.py
```

### 2. Verificar Instalación
```bash
# Verificar que la aplicación inicia correctamente
python -m app.main

# Verificar endpoints
curl http://localhost:8000/api/v1/products/inventory
curl http://localhost:8000/api/v1/recipes/
```

## 📈 Ejemplos de Uso

### Crear Materia Prima
```python
product_data = {
    "name": "Arroz 10KG",
    "product_type": "inventory",
    "purchase_price": 25.00,
    "stock_quantity": 50,
    "min_stock_level": 10,
    "unit": "kg"
}
```

### Crear Producto de Venta
```python
product_data = {
    "name": "Costilla en Salsa BBQ",
    "product_type": "sales",
    "price": 25.00,
    "unit": "plato"
}
```

### Crear Receta
```python
recipe_data = {
    "name": "Receta Costilla BBQ",
    "product_id": 1,  # ID del producto de venta
    "preparation_time": 45,
    "items": [
        {
            "product_id": 4,  # ID de la costilla
            "quantity": 0.5,
            "unit": "kg"
        }
    ]
}
```

### Verificar Disponibilidad
```python
availability = {
    "product_id": 1,  # Costilla BBQ
    "quantity": 2     # 2 platos
}
# Respuesta: {"available": true/false, "ingredients": [...]}
```

### Consumir Inventario
```python
consumption = {
    "product_id": 1,  # Costilla BBQ
    "quantity": 2,    # 2 platos
    "sale_id": 123    # ID de la venta
}
# Descuenta automáticamente 1kg de costilla
```

## 🎯 Beneficios

### Para el Restaurante
- **Control preciso** del inventario de materias primas
- **Prevención de desperdicios** por stock insuficiente
- **Cálculo automático** de costos de producción
- **Trazabilidad completa** de todos los movimientos

### Para la Gestión
- **Alertas automáticas** de stock bajo
- **Reportes detallados** de consumo
- **Optimización** de compras de materias primas
- **Control de costos** en tiempo real

### Para la Operación
- **Flujo simplificado** de ventas
- **Prevención de errores** de stock
- **Automatización** de procesos manuales
- **Integración** con el sistema POS existente

## 🔮 Próximas Mejoras

- [ ] **Interfaz web** para gestión de recetas
- [ ] **Reportes avanzados** de consumo
- [ ] **Integración con proveedores** para compras automáticas
- [ ] **Análisis de tendencias** de consumo
- [ ] **Optimización de menú** basada en costos
- [ ] **App móvil** para gestión de inventario

## 📞 Soporte

Para dudas o problemas con el nuevo sistema de inventario, consultar:
- Documentación de la API en `/docs`
- Logs de la aplicación
- Base de datos para verificar datos

---

**Versión**: 1.0.0  
**Fecha**: Diciembre 2024  
**Autor**: Sistema POS Team
