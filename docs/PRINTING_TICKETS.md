# Funcionalidad de Impresión de Tickets

## Descripción
El Sistema POS incluye una funcionalidad completa para imprimir tickets de venta. Esta característica permite generar tickets profesionales con toda la información relevante de la venta.

## Características

### 1. Botones de Acción
En la página de ventas, cada venta tiene tres botones de acción:
- **Ver detalles** (ojo): Muestra los detalles de la venta
- **Vista previa** (ojo lleno): Abre una vista previa del ticket
- **Imprimir** (impresora): Imprime directamente el ticket

### 2. Información del Ticket
El ticket incluye:
- **Encabezado**: Nombre del sistema y subtítulo
- **Información de la venta**: Número de ticket, fecha, cliente, vendedor
- **Productos**: Lista detallada con nombre, cantidad, precio unitario y total
- **Totales**: Subtotal, IVA (16%) y total final
- **Pie de página**: Mensaje de agradecimiento

### 3. Estilos de Impresión
- **Fuente**: Courier New (monoespaciada) para mejor legibilidad
- **Tamaño**: Optimizado para impresoras térmicas (80mm)
- **Formato**: Diseño profesional con líneas punteadas y espaciado adecuado

## Uso

### Imprimir un Ticket
1. Navega a la página de **Ventas**
2. Encuentra la venta que deseas imprimir
3. Haz clic en el botón **Imprimir** (ícono de impresora)
4. Confirma la impresión en el diálogo
5. El ticket se abrirá en una nueva ventana y se imprimirá automáticamente

### Vista Previa
1. Haz clic en el botón **Vista previa** (ícono de ojo lleno)
2. El ticket se abrirá en una nueva ventana para revisión
3. Puedes imprimir manualmente desde la ventana del navegador

## Configuración Técnica

### Endpoint API
```
GET /api/v1/sales/{sale_id}/print
```

### Archivos Relacionados
- `app/routers/sales.py`: Endpoint de impresión
- `templates/sales.html`: Interfaz de usuario
- `static/css/ticket.css`: Estilos del ticket

### Dependencias
- FastAPI para el endpoint
- Jinja2 para templates HTML
- Bootstrap Icons para iconos

## Personalización

### Modificar Estilos
Los estilos del ticket se encuentran en `static/css/ticket.css`. Puedes modificar:
- Fuentes y tamaños
- Colores y espaciado
- Ancho del ticket
- Elementos a mostrar/ocultar

### Agregar Información
Para agregar más información al ticket, edita la función `print_sale_ticket` en `app/routers/sales.py`.

### Cambiar Formato
El ticket está optimizado para impresoras térmicas de 80mm. Para otros formatos:
1. Modifica el ancho en el CSS
2. Ajusta el espaciado y tamaños de fuente
3. Considera la resolución de tu impresora

## Solución de Problemas

### Ventana Emergente Bloqueada
Si el navegador bloquea las ventanas emergentes:
1. Habilita las ventanas emergentes para tu sitio
2. Verifica la configuración del navegador
3. Intenta usar un navegador diferente

### Problemas de Impresión
- Verifica que la impresora esté conectada y funcionando
- Asegúrate de que el tamaño de papel sea correcto
- Revisa la configuración de márgenes en el navegador

### Ticket No Se Ve Correctamente
- Verifica que el archivo CSS se cargue correctamente
- Revisa la consola del navegador para errores
- Asegúrate de que la venta tenga datos válidos

## Mejoras Futuras

### Funcionalidades Sugeridas
- [ ] Impresión en lote de múltiples tickets
- [ ] Configuración personalizable del ticket
- [ ] Impresión directa a impresoras térmicas
- [ ] Generación de PDF
- [ ] Historial de tickets impresos
- [ ] Plantillas personalizables

### Integración con Hardware
- [ ] Soporte para cajones de dinero
- [ ] Impresión automática al completar venta
- [ ] Integración con escáneres de códigos de barras
- [ ] Soporte para pantallas de cliente
