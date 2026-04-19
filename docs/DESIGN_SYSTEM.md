# ZimplePOS - Sistema de Diseño

## Propuesta de Rediseño para Sistema POS de Restaurantes

---

## 1. Nueva Identidad Visual

### 1.1 Paleta de Colores

| Color | Hex | Uso |
|-------|-----|-----|
| **Primary (Esmeralda)** | `#10b981` | Acciones principales, success, dinero |
| Primary Light | `#d1fae5` | Fondos, badges |
| Primary Dark | `#047857` | emphasis |
| **Secondary (Naranja)** | `#f97316` | Highlights, advertencias, energía |
| Secondary Light | `#ffedd5` | Fondos secundarios |
| **Neutros** | `#f9fafb` | Background principal |
| | `#ffffff` | Cards, superficies |
| | `#1f2937` | Texto principal |
| | `#6b7280` | Texto secundario |

### 1.2 Colores Semánticos

| Color | Hex | Uso |
|-------|-----|-----|
| Success | `#10b981` | Pedidos completados, mesas disponibles |
| Warning | `#f59e0b` | Alertas, pedidos pendientes |
| Danger | `#ef4444` | Errores, cancelaciones |
| Info | `#3b82f6` | Información, reservaciones |

---

## 2. Tipografía

### Familia Principal
- **Inter** - Google Fonts
- weights: 300, 400, 500, 600, 700, 800

### Escala Tipográfica
| Elemento | Tamaño | Weight |
|----------|--------|--------|
| H1 | 2rem (32px) | 700 |
| H2 | 1.5rem (24px) | 600 |
| H3 | 1.25rem (20px) | 600 |
| Body | 1rem (16px) | 400 |
| Small | 0.875rem (14px) | 400 |
| Caption | 0.75rem (12px) | 400 |

---

## 3. Logo

### Descripción
Logo moderno y minimalista basado en:
- Letra "Z" estilizada
- Elemento de caja registradora/POS
- Colores: Esmeralda primario

### Variantes
- **Full**: Logo + texto "ZimplePOS"
- **Icon**: Solo el icono (para favicon, etc.)

---

## 4. Componentes Principales

### 4.1 Dashboard
- **Stats Cards**: 4 métricas principales en grid
  - Ventas del día (primary)
  - Pedidos del día (secondary)
  - Mesas activas (neutral)
  - Tiempo promedio (neutral)
- **Mesas Grid**: Visualización de estado de mesas
- **Pedidos Activos**: Lista lateral de pedidos recientes

### 4.2 Caja de Ventas (POS)
- **Layout**: 2 columnas (productos | pedido)
- **Categorías**: Tabs horizontales
- **Productos**: Grid de cards con imagen placeholder
- **Pedido Actual**: Panel derecho con items, totales, métodos de pago
- **Acciones**: Cobrar, guardar, limpiar

### 4.3 Estados de Mesa
| Estado | Color | Descripción |
|--------|-------|-------------|
| Disponible | Verde esmeralda | Mesa libre |
| Ocupada | Naranja | Con clientes activos |
| Reservada | Azul | Reservada para más tarde |
| Limpieza | Amarillo | Esperando limpieza |

---

## 5. Iconografía

### Biblioteca
- **Phosphor Icons** (PhosphorIcons.com)
- Estilo: Duotone/Regular
- Tamaño base: 24px

### Iconos Principales
| Módulo | Icono |
|--------|-------|
| Dashboard | ph-house |
| Caja | ph-cash-register |
| Meseros | ph-user |
| Cocina | ph-cooking-pot |
| Inventario | ph-package |
| Reportes | ph-chart-line-up |
| Configuración | ph-gear |
| Productos | ph-shopping-bag |

---

## 6. Tecnologías

### Frontend
- **TailwindCSS 3.x** - Utility-first CSS
- **Phosphor Icons** - Iconos
- **Google Fonts (Inter)** - Tipografía
- **Vanilla JS** - Interactividad

### Estructura de CSS
```
static/css/
├── zimplepos-theme.css     # Variables CSS y temas
└── components/
    └── ui-components.css   # Componentes reutilizables
```

---

## 7. Ejemplos de Código

### Botón Primary
```html
<button class="bg-primary-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-primary-600 transition-colors">
    Aceptar
</button>
```

### Card
```html
<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <h3 class="text-lg font-semibold">Título</h3>
    <p class="text-gray-500">Contenido</p>
</div>
```

### Badge
```html
<span class="bg-primary-100 text-primary-700 px-2.5 py-0.5 rounded-full text-xs font-medium">
    Activo
</span>
```

---

## 8. Responsive Design

### Breakpoints
| Breakpoint | Ancho | Uso |
|------------|-------|-----|
| sm | 640px | Móviles landscape |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktop |
| 2xl | 1536px | Large desktop |

### Estrategias
- **Mobile-first**: Diseñar para móvil primero
- **Flexbox**: Layout principal
- **Grid**: Grids de productos/mesas
- **Hidden**: Ocultar elementos no esenciales en móvil

---

## 9. Mejoras de UX

### Velocidad
- Carga rápida con TailwindCSS (purged)
- Imágenes optimizadas
- Iconos como SVG inline

### Claridad
- Espaciado consistente (4px base)
- Jerarquía visual clara
- Colores semánticos

### Accesibilidad
- Contraste WCAG AA
- Focus states visibles
- Labels en formularios

---

## 10. Archivos Creados

| Archivo | Descripción |
|---------|-------------|
| `static/css/zimplepos-theme.css` | Variables CSS y tema |
| `static/css/components/ui-components.css` | Componentes reutilizables |
| `static/images/logo-zimplepos.svg` | Logo del sistema |
| `templates/base_v2.html` | Template base nuevo |
| `templates/dashboard_v2.html` | Dashboard moderno |
| `templates/caja-ventas-v2.html` | Pantalla de ventas |

---

## Próximos Pasos

1. Integrar templates con backend FastAPI
2. Migrar más páginas al nuevo diseño
3. Agregar más componentes (modales, tablas, etc.)
4. Optimizar performance
5. Agregar tests de diseño

---

*Documento generado para ZimplePOS - Sistema POS para Restaurantes*
