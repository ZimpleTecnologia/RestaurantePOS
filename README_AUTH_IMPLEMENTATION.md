# Implementación del Sistema de Autenticación y Timeout de Sesión

## Resumen de Cambios

Se ha implementado un sistema completo de autenticación y timeout de sesión por inactividad para el Sistema POS. Este sistema resuelve el problema de que la aplicación se abría directamente al dashboard sin verificar autenticación.

## Archivos Modificados/Creados

### 1. Nuevo Middleware de Autenticación (`app/middleware.py`)
- **AuthMiddleware**: Verifica la autenticación en todas las páginas HTML
- **SessionTimeoutMiddleware**: Maneja el timeout de sesión por inactividad
- Redirige automáticamente al login si no hay token válido

### 2. Archivo Principal Actualizado (`app/main.py`)
- Se agregaron los middlewares de autenticación
- Ahora todas las páginas están protegidas por defecto

### 3. Configuración Actualizada (`app/config.py`)
- Nuevas configuraciones para timeout de sesión:
  - `session_timeout_minutes`: 30 minutos (configurable)
  - `session_warning_minutes`: 2 minutos antes del timeout
  - `session_check_interval`: 60 segundos entre verificaciones

### 4. Sistema de Autenticación Frontend (`static/js/auth.js`)
- Verificación automática de autenticación
- Timer de inactividad configurable
- Advertencias antes del timeout
- Detección de actividad del usuario
- Verificación de expiración del token

### 5. Templates Actualizados
- `base.html`: Incluye el sistema de autenticación
- `login.html`: Guarda tokens en cookies y localStorage

## Funcionalidades Implementadas

### ✅ Verificación de Autenticación
- Cada página verifica si existe un token válido
- Redirección automática al login si no hay sesión
- Protección de todas las rutas excepto login y APIs

### ✅ Timeout por Inactividad
- Sesión se cierra automáticamente después de 30 minutos sin actividad
- Advertencia 2 minutos antes del timeout
- Posibilidad de extender la sesión

### ✅ Detección de Actividad
- Monitorea movimientos del mouse, teclado, scroll, etc.
- Resetea el timer con cada actividad del usuario
- Funciona en múltiples pestañas

### ✅ Gestión de Tokens
- Verificación de expiración del token JWT
- Advertencias cuando el token está próximo a expirar
- Limpieza automática de tokens expirados

## Configuración

### Variables de Entorno
```bash
# Timeout de sesión (en minutos)
SESSION_TIMEOUT_MINUTES=30
SESSION_WARNING_MINUTES=2
SESSION_CHECK_INTERVAL=60

# Expiración del token JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Personalización
- El timeout se puede configurar desde el servidor
- Las advertencias son configurables
- El intervalo de verificación es ajustable

## Cómo Funciona

### 1. Al Cargar una Página
- Se verifica si existe un token válido
- Si no hay token → redirección al login
- Si hay token → se inicia el timer de inactividad

### 2. Durante la Navegación
- Cada actividad del usuario resetea el timer
- Se verifica periódicamente la expiración del token
- Se muestran advertencias cuando es necesario

### 3. Al Expirar la Sesión
- Se muestra una advertencia 2 minutos antes
- El usuario puede extender la sesión
- Si no se extiende → cierre automático y redirección al login

## Beneficios

1. **Seguridad**: Todas las páginas están protegidas
2. **Experiencia de Usuario**: Advertencias claras antes del timeout
3. **Flexibilidad**: Configuración ajustable desde el servidor
4. **Robustez**: Manejo de múltiples escenarios de expiración
5. **Mantenibilidad**: Código modular y bien organizado

## Próximos Pasos Recomendados

1. **Configurar variables de entorno** en producción
2. **Ajustar timeouts** según las necesidades del negocio
3. **Implementar logging** de eventos de sesión
4. **Agregar métricas** de uso de sesiones
5. **Considerar refresh tokens** para sesiones más largas

## Solución de Problemas

### La aplicación sigue abriendo el dashboard
- Verificar que el middleware esté activo
- Comprobar que no haya tokens en localStorage/cookies
- Revisar la consola del navegador para errores

### El timeout no funciona
- Verificar que auth.js esté cargando correctamente
- Comprobar las configuraciones del servidor
- Revisar la consola para mensajes de error

### Problemas con cookies
- Verificar la configuración de SameSite
- Comprobar que el dominio sea correcto
- Revisar la configuración de HTTPS en producción

## Notas Técnicas

- El sistema usa tanto localStorage como cookies para compatibilidad
- Los middlewares se ejecutan en orden: AuthMiddleware → SessionTimeoutMiddleware
- La detección de actividad es eficiente y no impacta el rendimiento
- El sistema es compatible con múltiples navegadores

