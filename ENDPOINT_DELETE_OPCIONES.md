# 📋 Documentación: Endpoint DELETE para Opciones de Platos

## 🎯 Resumen del Cambio

Se ha corregido el error **405 Method Not Allowed** implementando una lógica inteligente de eliminación/desactivación para las opciones de platos.

---

## 🔧 Endpoints Implementados

### 1. DELETE `/api/v1/menu-restructured/opciones/{opcion_id}`

**Funcionalidad Inteligente:**
- ✅ **Si la opción NO está en uso**: Se elimina permanentemente de la base de datos
- ⚠️ **Si la opción SÍ está en uso**: Se desactiva automáticamente (soft delete)

#### Ejemplo de Uso:

```bash
# Intentar eliminar una opción
curl -X DELETE http://localhost:8000/api/v1/menu-restructured/opciones/45
```

#### Respuestas Posibles:

##### **Caso 1: Opción Desactivada (está en uso)**
```json
{
  "success": true,
  "action": "deactivated",
  "message": "La opción ha sido desactivada porque está siendo usada en 4 menú(s).",
  "menu_count": 4,
  "warning": "El plato ya no aparecerá en nuevos menús, pero permanece en los menús existentes. Para eliminarlo completamente, remuévalo de todos los menús primero.",
  "opcion": {
    "id": 45,
    "nombre": "Arroz con Pollo",
    "activo": false
  }
}
```

##### **Caso 2: Opción ya Desactivada**
```json
{
  "success": true,
  "action": "already_inactive",
  "message": "La opción ya estaba desactivada. Está siendo usada en 4 menú(s).",
  "menu_count": 4,
  "warning": "Para eliminarla completamente, primero remuévala de todos los menús donde está siendo utilizada."
}
```

##### **Caso 3: Opción Eliminada Permanentemente (no está en uso)**
```json
{
  "success": true,
  "action": "deleted",
  "message": "Opción eliminada permanentemente"
}
```

##### **Caso 4: Opción No Encontrada**
```json
{
  "detail": "Opción no encontrada"
}
```
*Status Code: 404*

---

### 2. PATCH `/api/v1/menu-restructured/opciones/{opcion_id}/toggle-status`

**Funcionalidad:**
Permite activar/desactivar manualmente una opción sin eliminarla.

#### Ejemplo de Uso:

```bash
# Cambiar el estado de una opción
curl -X PATCH http://localhost:8000/api/v1/menu-restructured/opciones/45/toggle-status
```

#### Respuesta:

```json
{
  "success": true,
  "message": "Opción activada exitosamente",
  "opcion": {
    "id": 45,
    "nombre": "Arroz con Pollo",
    "activo": true
  }
}
```

---

## 📊 Flujo de Trabajo Recomendado

### Escenario 1: Eliminar un Plato No Usado
```
1. Usuario hace clic en "Eliminar"
2. Sistema verifica: ¿Está en menús? → NO
3. Sistema elimina permanentemente
4. ✅ Plato eliminado de la BD
```

### Escenario 2: Eliminar un Plato en Uso
```
1. Usuario hace clic en "Eliminar"
2. Sistema verifica: ¿Está en menús? → SÍ (4 menús)
3. Sistema desactiva el plato automáticamente
4. ⚠️ Plato desactivado (soft delete)
5. Frontend muestra mensaje:
   "Este plato está siendo usado en 4 menú(s).
    Ha sido desactivado y no aparecerá en nuevos menús.
    Para eliminarlo completamente, remuévalo de los menús existentes."
```

### Escenario 3: Reactivar un Plato
```
1. Usuario hace clic en "Activar"
2. Sistema ejecuta PATCH /toggle-status
3. ✅ Plato reactivado
```

---

## 🎨 Integración en el Frontend

### Ejemplo de Código JavaScript

```javascript
// Función para eliminar una opción
async function deleteOpcion(opcionId) {
    try {
        const response = await fetch(
            `/api/v1/menu-restructured/opciones/${opcionId}`,
            { method: 'DELETE' }
        );
        
        const data = await response.json();
        
        if (data.success) {
            switch(data.action) {
                case 'deleted':
                    showSuccess('Plato eliminado permanentemente');
                    refreshTable();
                    break;
                    
                case 'deactivated':
                    showWarning(
                        `${data.message}\n\n${data.warning}`,
                        `Menús afectados: ${data.menu_count}`
                    );
                    refreshTable();
                    break;
                    
                case 'already_inactive':
                    showInfo(
                        `${data.message}\n\n${data.warning}`,
                        `Menús afectados: ${data.menu_count}`
                    );
                    break;
            }
        }
    } catch (error) {
        showError('Error al eliminar el plato: ' + error.message);
    }
}

// Función para activar/desactivar
async function toggleOpcionStatus(opcionId) {
    try {
        const response = await fetch(
            `/api/v1/menu-restructured/opciones/${opcionId}/toggle-status`,
            { method: 'PATCH' }
        );
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            refreshTable();
        }
    } catch (error) {
        showError('Error al cambiar estado: ' + error.message);
    }
}
```

---

## 🧪 Testing

### Prueba Automática
```bash
# Ejecutar el script de prueba
python test_delete_opcion.py
```

### Prueba Manual con cURL

```bash
# 1. Listar todas las opciones
curl http://localhost:8000/api/v1/menu-restructured/opciones/

# 2. Intentar eliminar una opción específica
curl -X DELETE http://localhost:8000/api/v1/menu-restructured/opciones/45

# 3. Verificar el estado actual
curl http://localhost:8000/api/v1/menu-restructured/opciones/

# 4. Reactivar la opción
curl -X PATCH http://localhost:8000/api/v1/menu-restructured/opciones/45/toggle-status

# 5. Verificar que fue reactivada
curl http://localhost:8000/api/v1/menu-restructured/opciones/
```

---

## 🔍 Logs del Sistema

Cuando se ejecuta una eliminación, verás logs como estos:

```
🗑️ Intentando eliminar opción ID: 45
⚠️ Opción 45 está siendo usada en 4 menú(s) - Desactivando...
✅ Opción 45 desactivada exitosamente
```

O si no está en uso:

```
🗑️ Intentando eliminar opción ID: 99
✅ Opción 99 no está en uso - Eliminando permanentemente...
✅ Opción 99 eliminada exitosamente
```

---

## ✅ Ventajas de Esta Implementación

1. **Seguridad**: No rompe la integridad referencial
2. **Transparencia**: El usuario sabe exactamente qué pasó
3. **Flexibilidad**: Permite desactivar temporalmente sin eliminar
4. **Reversibilidad**: Los platos desactivados pueden reactivarse
5. **Auditoría**: Mantiene el historial de menús previos

---

## 🚀 Próximos Pasos

### Recomendaciones:

1. **Filtrar platos inactivos** en el listado principal (mostrar solo activos por defecto)
2. **Agregar filtro** "Ver platos inactivos" para administradores
3. **Implementar endpoint** para forzar eliminación (solo ADMIN)
4. **Agregar indicador visual** en el frontend para platos desactivados
5. **Crear reporte** de platos desactivados que pueden eliminarse

---

## 📝 Notas Técnicas

- El campo `activo` en el modelo `OpcionPlato` se usa para el soft delete
- La tabla `menu_dia_opciones` mantiene las relaciones existentes
- Los logs usan emojis para facilitar el debugging visual
- Las transacciones tienen rollback automático en caso de error

---

**Autor:** Sistema de Gestión de Menús  
**Fecha:** Octubre 2025  
**Versión:** 1.0
