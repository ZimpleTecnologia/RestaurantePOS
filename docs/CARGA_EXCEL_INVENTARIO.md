# Carga de Inventario desde Excel

Esta funcionalidad permite cargar productos al inventario desde un archivo Excel, facilitando la gestión masiva de productos en el sistema.

## Características

- ✅ Carga masiva de productos desde archivo Excel (.xlsx, .xls)
- ✅ Validación automática de datos
- ✅ Creación automática de categorías faltantes
- ✅ Actualización de productos existentes
- ✅ Creación automática de movimientos de stock inicial
- ✅ Plantilla descargable con formato correcto
- ✅ Reporte detallado de resultados

## Campos del Excel

### Campos Obligatorios

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `nombre` | Texto | Nombre del producto | "Hamburguesa Clásica" |
| `precio` | Decimal | Precio de venta | 12.50 |
| `categoria_id` | Entero | ID de la categoría | 1 |
| `stock_actual` | Entero | Cantidad inicial en inventario | 50 |
| `precio_compra` | Decimal | Precio de compra | 8.00 |

### Campos Opcionales

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `descripcion` | Texto | Descripción del producto | "Hamburguesa con carne, lechuga, tomate y queso" |
| `codigo_barras` | Texto | Código de barras | "1234567890123" |
| `sku` | Texto | Código SKU interno | "HAMB001" |
| `punto_reorden` | Entero | Cantidad mínima para reordenar | 10 |
| `cantidad_reorden` | Entero | Cantidad a ordenar | 30 |
| `unidad_medida` | Texto | Unidad de medida | "unidades" |
| `peso` | Decimal | Peso en kg | 0.3 |
| `dimensiones` | Texto | Dimensiones del producto | "15x10x5 cm" |
| `ubicacion_default` | Texto | Ubicación por defecto | "Refrigerador" |
| `fecha_vencimiento` | Fecha | Fecha de vencimiento | "2024-12-31" |
| `lote` | Texto | Número de lote | "LOT001" |
| `proveedor` | Texto | Nombre del proveedor | "Carnes Premium" |

## Categorías Predefinidas

| ID | Nombre | Descripción |
|----|--------|-------------|
| 1 | Comida | Platos principales y acompañamientos |
| 2 | Bebida | Bebidas y refrescos |
| 3 | Postre | Postres y dulces |
| 4 | Entrada | Entradas y aperitivos |
| 5 | Especial | Platos especiales del día |

## Instrucciones de Uso

### 1. Acceder a la Funcionalidad

1. Ve al módulo de **Inventario**
2. Haz clic en el botón **"Cargar Excel"** (ícono de archivo Excel)
3. Se abrirá el modal de carga

### 2. Descargar Plantilla (Opcional)

1. En el modal, haz clic en **"Descargar Plantilla"**
2. Se descargará un archivo Excel con:
   - Hoja "Inventario": Datos de ejemplo
   - Hoja "Instrucciones": Guía completa
   - Hoja "Categorías": Lista de categorías disponibles

### 3. Preparar el Archivo Excel

1. Usa la plantilla como base o crea tu propio archivo
2. Asegúrate de que la primera fila contenga los nombres de las columnas
3. Completa los campos obligatorios para cada producto
4. Agrega campos opcionales según necesites

### 4. Configurar Opciones

En el modal, puedes configurar:

- ✅ **Crear categorías automáticamente**: Si no existe una categoría, se creará automáticamente
- ✅ **Actualizar productos existentes**: Si un producto ya existe (por nombre), se actualizará
- ✅ **Crear movimiento de stock inicial**: Se creará un movimiento de entrada con el stock inicial

### 5. Cargar el Archivo

1. Haz clic en **"Seleccionar archivo Excel"**
2. Busca y selecciona tu archivo Excel
3. Haz clic en **"Cargar Inventario"**
4. Espera a que se procese el archivo
5. Revisa los resultados del procesamiento

## Validaciones Automáticas

El sistema valida automáticamente:

- ✅ Campos obligatorios presentes
- ✅ Tipos de datos correctos (números, fechas, etc.)
- ✅ Existencia de categorías (si no se permite crear automáticamente)
- ✅ Formato de fechas (YYYY-MM-DD)
- ✅ Valores numéricos válidos

## Reporte de Resultados

Después de la carga, se muestra un reporte con:

- 📊 **Productos creados**: Cantidad de productos nuevos
- 📊 **Productos actualizados**: Cantidad de productos modificados
- 📊 **Categorías creadas**: Categorías creadas automáticamente
- 📊 **Movimientos de stock**: Movimientos de entrada creados
- ⚠️ **Errores**: Lista de errores encontrados (si los hay)

## Ejemplo de Archivo Excel

```excel
nombre              | precio | categoria_id | stock_actual | precio_compra | descripcion
Hamburguesa Clásica | 12.50  | 1            | 50           | 8.00          | Hamburguesa con carne
Coca Cola 500ml     | 2.50   | 2            | 100          | 1.80          | Refresco Coca Cola
```

## Permisos Requeridos

Para usar esta funcionalidad necesitas uno de estos roles:
- 👑 **ADMIN**
- 📦 **ALMACEN**
- 👨‍💼 **SUPERVISOR**

## Solución de Problemas

### Error: "Campo 'nombre' es obligatorio"
- Verifica que la primera fila contenga los nombres de las columnas
- Asegúrate de que no haya filas vacías

### Error: "Categoría con ID X no existe"
- Verifica que el ID de categoría sea correcto
- Activa la opción "Crear categorías automáticamente"

### Error: "El precio debe ser un número válido"
- Usa punto como separador decimal (12.50, no 12,50)
- No incluyas símbolos de moneda

### Error: "Formato de fecha inválido"
- Usa formato YYYY-MM-DD (2024-12-31)
- No uses barras ni otros separadores

## API Endpoint

```http
POST /api/v1/inventory/upload-excel
Content-Type: application/json

{
  "products": [
    {
      "nombre": "Producto Ejemplo",
      "precio": 10.00,
      "categoria_id": 1,
      "stock_actual": 25,
      "precio_compra": 7.00
    }
  ],
  "options": {
    "create_missing_categories": true,
    "update_existing_products": true,
    "create_initial_stock": true
  }
}
```

## Archivos Relacionados

- `templates/inventory.html`: Interfaz de usuario
- `app/routers/inventory.py`: Endpoint de la API
- `create_excel_template.py`: Script para generar plantilla
- `app/services/inventory_service.py`: Lógica de negocio

## Notas Técnicas

- El archivo se procesa en el frontend usando SheetJS
- Los datos se envían al backend en formato JSON
- Se crean transacciones de base de datos para cada producto
- Se registran logs de todas las operaciones
- El sistema maneja errores de forma robusta y continúa procesando
