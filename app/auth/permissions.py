"""
Sistema de verificación de permisos
Middleware y dependencias para control de acceso basado en permisos
"""
from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.dependencies import get_current_active_user


def verificar_permiso(codigo_permiso: str):
    """
    Dependency para verificar que el usuario actual tiene un permiso específico.
    Los usuarios ADMIN tienen todos los permisos automáticamente.
    
    Args:
        codigo_permiso: Código del permiso requerido (ej: "mesas", "usuarios", "cocina")
    
    Returns:
        Función dependency que verifica el permiso
    
    Raises:
        HTTPException: Si el usuario no tiene el permiso requerido
    
    Ejemplo de uso:
        @router.get("/mesas/", dependencies=[Depends(verificar_permiso("mesas"))])
        def get_mesas(...):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        # Admin tiene todos los permisos
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        # Verificar permiso específico
        if not current_user.tiene_permiso(codigo_permiso):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso para acceder a este recurso. Permiso requerido: '{codigo_permiso}'"
            )
        
        return current_user
    
    return permission_checker


def verificar_cualquier_permiso(codigos_permisos: List[str]):
    """
    Dependency para verificar que el usuario tiene AL MENOS UNO de los permisos especificados.
    Los usuarios ADMIN tienen todos los permisos automáticamente.
    
    Args:
        codigos_permisos: Lista de códigos de permisos (el usuario necesita al menos uno)
    
    Returns:
        Función dependency que verifica los permisos
    
    Raises:
        HTTPException: Si el usuario no tiene ninguno de los permisos requeridos
    
    Ejemplo de uso:
        @router.get("/reportes/", dependencies=[Depends(verificar_cualquier_permiso(["reportes", "ventas"]))])
        def get_reportes(...):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        # Admin tiene todos los permisos
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        # Verificar si tiene al menos uno de los permisos
        tiene_alguno = any(
            current_user.tiene_permiso(codigo) for codigo in codigos_permisos
        )
        
        if not tiene_alguno:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos para acceder a este recurso. Se requiere al menos uno de: {', '.join(codigos_permisos)}"
            )
        
        return current_user
    
    return permission_checker


def verificar_todos_permisos(codigos_permisos: List[str]):
    """
    Dependency para verificar que el usuario tiene TODOS los permisos especificados.
    Los usuarios ADMIN tienen todos los permisos automáticamente.
    
    Args:
        codigos_permisos: Lista de códigos de permisos (el usuario necesita todos)
    
    Returns:
        Función dependency que verifica los permisos
    
    Raises:
        HTTPException: Si el usuario no tiene todos los permisos requeridos
    
    Ejemplo de uso:
        @router.post("/operacion-critica/", dependencies=[Depends(verificar_todos_permisos(["ventas", "inventario"]))])
        def operacion_critica(...):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        # Admin tiene todos los permisos
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        # Verificar que tiene todos los permisos
        permisos_faltantes = [
            codigo for codigo in codigos_permisos
            if not current_user.tiene_permiso(codigo)
        ]
        
        if permisos_faltantes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes todos los permisos requeridos. Faltan: {', '.join(permisos_faltantes)}"
            )
        
        return current_user
    
    return permission_checker


# Aliases para permisos específicos comunes
require_mesas_permission = verificar_permiso("mesas")
require_usuarios_permission = verificar_permiso("usuarios")
require_cocina_permission = verificar_permiso("cocina")
require_ventas_permission = verificar_permiso("ventas")
require_caja_permission = verificar_permiso("caja")
require_inventario_permission = verificar_permiso("inventario")
require_reportes_permission = verificar_permiso("reportes")
require_meseros_permission = verificar_permiso("meseros")


def usuario_puede_modificar_usuario(usuario_objetivo_id: int):
    """
    Verifica si el usuario actual puede modificar a otro usuario.
    Reglas:
    - ADMIN puede modificar a cualquiera
    - Un usuario puede modificar solo su propia información básica
    
    Args:
        usuario_objetivo_id: ID del usuario que se quiere modificar
    
    Returns:
        True si puede modificar, False en caso contrario
    """
    async def checker(
        current_user: User = Depends(get_current_active_user)
    ):
        # Admin puede modificar a cualquiera
        if current_user.role == UserRole.ADMIN:
            return True
        
        # Un usuario solo puede modificar su propia información
        if current_user.id == usuario_objetivo_id:
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar este usuario"
        )
    
    return checker

