"""
Middleware para restringir acceso a usuarios de inventario
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.models.user import UserRole

class InventoryAccessMiddleware(BaseHTTPMiddleware):
    """Middleware para restringir acceso de usuarios de inventario"""
    
    # Rutas permitidas para usuarios de inventario
    ALLOWED_PATHS = [
        "/",
        "/login",
        "/logout",
        "/inventory",
        "/api/v1/inventory",
        "/api/v1/auth",
        "/static",
        "/uploads",
        "/health",
        "/api/v1/",
        "/docs",
        "/redoc"
    ]
    
    # Rutas que requieren mensaje de "trabajando en progreso"
    RESTRICTED_PATHS = [
        "/products",
        "/admin",
        "/caja-ventas",
        "/cash-register",
        "/waiters",
        "/kitchen",
        "/reports",
        "/settings",
        "/recipes",
        "/api/v1/products",
        "/api/v1/caja-ventas",
        "/api/v1/waiters",
        "/api/v1/kitchen",
        "/api/v1/reports",
        "/api/v1/settings",
        "/api/v1/recipes",
        "/api/v1/menu",
        "/api/v1/carta_restaurante"
    ]
    
    async def dispatch(self, request: Request, call_next):
        """Procesar request y verificar permisos"""
        
        # Obtener usuario de la sesión (si existe)
        user_role = None
        if hasattr(request.state, 'user') and request.state.user:
            user_role = request.state.user.role
        
        # Si es usuario de inventario, aplicar restricciones
        if user_role == UserRole.ALMACEN:
            path = request.url.path
            
            # Verificar si la ruta está permitida
            is_allowed = any(path.startswith(allowed) for allowed in self.ALLOWED_PATHS)
            
            if not is_allowed:
                # Verificar si es una ruta restringida
                is_restricted = any(path.startswith(restricted) for restricted in self.RESTRICTED_PATHS)
                
                if is_restricted:
                    # Redirigir a página de desarrollo
                    from fastapi.responses import RedirectResponse
                    return RedirectResponse(url="/module-development", status_code=302)
                else:
                    # Para otras rutas, denegar acceso
                    raise HTTPException(
                        status_code=403,
                        detail="Acceso denegado. Solo tienes permisos para el módulo de inventario."
                    )
        
        # Continuar con el request normal
        response = await call_next(request)
        return response
