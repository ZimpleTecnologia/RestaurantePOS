"""
Middleware de autenticación para el sistema POS
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import time
from typing import Optional
from app.auth.security import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware para verificar autenticación en páginas protegidas"""
    
    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/",
            "/login",
            "/api/v1/auth/login",
            "/api/v1/auth/login-json",
            "/api/v1/settings/",
            "/api/v1/settings/business-info",
            "/api/v1/settings/cash-register-config",
            "/api/v1/products/",
            "/api/v1/products/categories",
            "/api/v1/products/subcategories",
            "/api/v1/caja-ventas/estado",
            "/api/v1/caja-ventas/movimientos",
            "/static",
            "/uploads",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Verificar si la ruta está excluida de autenticación
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Para rutas de API, usar el sistema de dependencias existente
        if request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Para páginas HTML, verificar token en cookies o headers
        token = self._extract_token(request)
        
        if not token:
            # No hay token, redirigir al login
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
        # Verificar si el token es válido
        username = verify_token(token)
        if not username:
            # Token inválido, redirigir al login
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
        # Token válido, continuar
        return await call_next(request)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extraer token de cookies o headers"""
        # Buscar en cookies primero
        token = request.cookies.get("auth_token")
        if token:
            return token
        
        # Buscar en headers de autorización
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        
        return None


class SessionTimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware para manejar timeout de sesión por inactividad"""
    
    def __init__(self, app, timeout_minutes: int = 30):
        super().__init__(app)
        self.timeout_minutes = timeout_minutes
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Solo aplicar a páginas HTML (no a APIs)
        if not request.url.path.startswith("/api/"):
            token = self._extract_token(request)
            if token:
                # Verificar si el token ha expirado por inactividad
                if self._is_token_expired_by_inactivity(token):
                    # Token expirado por inactividad, redirigir al login
                    response = RedirectResponse(url="/login?reason=timeout", status_code=status.HTTP_302_FOUND)
                    response.delete_cookie("auth_token")
                    return response
        
        return await call_next(request)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extraer token de cookies"""
        return request.cookies.get("auth_token")
    
    def _is_token_expired_by_inactivity(self, token: str) -> bool:
        """Verificar si el token ha expirado por inactividad"""
        try:
            # Decodificar el token para obtener la fecha de expiración
            from jose import jwt
            from app.config import settings
            
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            exp_timestamp = payload.get("exp")
            
            if not exp_timestamp:
                return True
            
            # Verificar si ha expirado
            current_time = time.time()
            return current_time > exp_timestamp
            
        except Exception:
            return True
