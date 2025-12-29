# Paquete de autenticación y seguridad

from .dependencies import (
    get_current_user,
    get_current_active_user,
    require_admin,
    require_supervisor_or_admin,
    require_waiter_or_admin
)

from .security import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password
)

from .permissions import (
    verificar_permiso,
    verificar_cualquier_permiso,
    verificar_todos_permisos,
    require_mesas_permission,
    require_usuarios_permission,
    require_cocina_permission,
    require_ventas_permission,
    require_caja_permission,
    require_inventario_permission,
    require_reportes_permission,
    require_meseros_permission,
    usuario_puede_modificar_usuario
)

__all__ = [
    "get_current_user",
    "get_current_active_user", 
    "require_admin",
    "require_supervisor_or_admin",
    "require_waiter_or_admin",
    "create_access_token",
    "verify_token",
    "get_password_hash",
    "verify_password",
    "verificar_permiso",
    "verificar_cualquier_permiso",
    "verificar_todos_permisos",
    "require_mesas_permission",
    "require_usuarios_permission",
    "require_cocina_permission",
    "require_ventas_permission",
    "require_caja_permission",
    "require_inventario_permission",
    "require_reportes_permission",
    "require_meseros_permission",
    "usuario_puede_modificar_usuario"
] 