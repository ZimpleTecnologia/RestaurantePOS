---
description: Actualiza automáticamente los estilos de la aplicación para aplicar una paleta visual tecnológica e innovadora basada en especializado en branding gastronómico premium.
---

Aplicar sistema de diseño visual coherente basado en una paleta gastronómica premium al sitio web

Pasos:

1. Auditoría visual:
   - Analizar todos los estilos (CSS, variables, inline)
   - Identificar colores, inconsistencias y patrones actuales

2. Definición de sistema de color (Design Tokens):
   - Primary: #7A1E2C
   - Secondary: #5C3A21
   - Background: #F2E8D5
   - Surface: #FFFFFF / variaciones beige
   - Text Primary: #2B2B2B
   - Text Secondary: #A67C52
   - Border: #8A8F94
   - Accent: #B87333 / #C9A66B

3. Crear variables CSS globales:
   - Definir tokens reutilizables (:root)
   - Incluir variantes (hover, active, disabled)

4. Aplicación del sistema:
   - Reemplazar colores existentes por tokens
   - Mapear:
     - Botones → primary
     - Cards → surface
     - Background → background
     - Links → primary/secondary

5. Estados interactivos:
   - Hover: oscurecer 10%
   - Active: oscurecer 15%
   - Focus: outline accesible
   - Disabled: reducir contraste

6. Ajuste de superficies:
   - Diferenciar background, cards, navbar y modales
   - Aplicar sombras suaves y profundidad

7. Validación UX/UI:
   - Revisar contraste (WCAG)
   - Asegurar legibilidad en todos los componentes
   - Evitar saturación visual

8. Consistencia visual:
   - Revisar coherencia en todo el sistema
   - Unificar estilos de botones, inputs y cards

9. Output:
   - Resumen de cambios
   - Lista de tokens definidos
   - Comparación antes/después