"""
Router para gestión de Usuarios/Meseros
Endpoints CRUD completos para el módulo de usuarios
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, UserPasswordReset
)
from app.auth import (
    get_current_active_user, require_admin, get_password_hash
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=UserListResponse, summary="Listar todos los usuarios")
def get_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    role: Optional[UserRole] = Query(None, description="Filtrar por rol"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado"),
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la lista de todos los usuarios del sistema.
    
    **Permisos requeridos**: Usuario activo
    
    **Parámetros**:
    - skip: Registros a saltar para paginación
    - limit: Máximo de registros a devolver
    - role: Filtrar por rol (opcional)
    - is_active: Filtrar por estado (opcional)
    - search: Buscar por nombre o email (opcional)
    
    **Retorna**: Lista de usuarios con permisos incluidos
    """
    try:
        from sqlalchemy import text
        
        # Consultar usuarios usando SQL crudo para evitar errores con roles inválidos
        # Construir la consulta SQL dinámicamente
        where_conditions = []
        params = {}
        
        if role:
            where_conditions.append("role::text = :role")
            params['role'] = role.value
        
        if is_active is not None:
            where_conditions.append("is_active = :is_active")
            params['is_active'] = is_active
        
        if search:
            where_conditions.append("(LOWER(full_name) LIKE :search OR LOWER(email) LIKE :search OR LOWER(username) LIKE :search)")
            params['search'] = f"%{search.lower()}%"
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Consulta para obtener total
        count_sql = text(f"SELECT COUNT(*) FROM users WHERE {where_clause}")
        total_result = db.execute(count_sql, params)
        total = total_result.scalar()
        
        # Consulta para obtener usuarios
        sql = text(f"""
            SELECT id, username, email, full_name, telefono, 
                   role::text as role_str, is_active, is_verified,
                   created_at, updated_at, last_login, hashed_password
            FROM users
            WHERE {where_clause}
            ORDER BY full_name
            LIMIT :limit OFFSET :offset
        """)
        params['limit'] = limit
        params['offset'] = skip
        
        result = db.execute(sql, params)
        rows = result.fetchall()
        
        # Convertir filas a objetos User, manejando roles inválidos
        usuarios_validos = []
        roles_validos = {r.value for r in UserRole}
        
        for row in rows:
            try:
                user_id, username, email, full_name, telefono, role_str, is_active_val, is_verified_val, created_at, updated_at, last_login, hashed_password = row
                
                # Verificar y corregir rol inválido
                if role_str not in roles_validos:
                    # Migrar rol inválido a MESERO
                    print(f"⚠️ Migrando usuario {username} (ID: {user_id}) de rol '{role_str}' a 'MESERO'")
                    db.execute(
                        text("UPDATE users SET role = :new_role WHERE id = :user_id"),
                        {'new_role': UserRole.MESERO.value, 'user_id': user_id}
                    )
                    db.commit()
                    role_str = UserRole.MESERO.value
                
                # Crear objeto User
                usuario = User(
                    id=user_id,
                    username=username,
                    email=email,
                    full_name=full_name,
                    telefono=telefono,
                    role=UserRole(role_str),
                    is_active=is_active_val,
                    is_verified=is_verified_val,
                    created_at=created_at,
                    updated_at=updated_at,
                    last_login=last_login,
                    hashed_password=hashed_password
                )
                usuarios_validos.append(usuario)
                
            except Exception as e:
                print(f"⚠️ Error procesando usuario ID {row[0] if row else 'desconocido'}: {e}")
                continue
        
        return UserListResponse(usuarios=usuarios_validos, total=total)
        
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = f"Error al obtener usuarios: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/me", response_model=UserResponse, summary="Obtener usuario actual")
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la información del usuario actualmente autenticado.
    
    **Permisos requeridos**: Usuario activo
    
    **Retorna**: Información del usuario con sus permisos
    """
    return current_user


@router.get("/{usuario_id}", response_model=UserResponse, summary="Obtener un usuario específico")
def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene los detalles de un usuario específico por su ID.
    
    **Permisos requeridos**: Usuario activo (puede ver su propia info o cualquiera si es ADMIN)
    
    **Parámetros**:
    - usuario_id: ID del usuario
    
    **Retorna**: Datos del usuario con permisos
    """
    # Solo admin puede ver otros usuarios
    if current_user.id != usuario_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver información de otros usuarios"
        )
    
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    return usuario


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Crear nuevo usuario")
def create_usuario(
    usuario: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Crea un nuevo usuario/mesero en el sistema.
    
    **Permisos requeridos**: ADMIN
    
    **Parámetros**:
    - usuario: Datos del usuario a crear
    
    **Retorna**: Usuario creado
    """
    try:
        # Verificar que no exista un usuario con el mismo username o email
        existing_username = db.query(User).filter(User.username == usuario.username.lower()).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un usuario con el nombre de usuario '{usuario.username}'"
            )
        
        existing_email = db.query(User).filter(User.email == usuario.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un usuario con el email '{usuario.email}'"
            )
        
        # Crear usuario con contraseña hasheada
        user_data = usuario.model_dump(exclude={'password'})
        user_data['username'] = user_data['username'].lower()
        user_data['hashed_password'] = get_password_hash(usuario.password)
        
        db_usuario = User(**user_data)
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        
        return db_usuario
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad: El usuario o email ya existe"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el usuario: {str(e)}"
        )


@router.put("/{usuario_id}", response_model=UserResponse, summary="Actualizar usuario")
def update_usuario(
    usuario_id: int,
    usuario_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Actualiza los datos de un usuario existente.
    
    **Permisos requeridos**: ADMIN
    
    **Parámetros**:
    - usuario_id: ID del usuario a actualizar
    - usuario_update: Datos a actualizar
    
    **Retorna**: Usuario actualizado
    """
    try:
        # Buscar el usuario
        db_usuario = db.query(User).filter(User.id == usuario_id).first()
        if not db_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Verificar unicidad de username si se está cambiando
        if usuario_update.username and usuario_update.username.lower() != db_usuario.username:
            existing = db.query(User).filter(
                User.username == usuario_update.username.lower(),
                User.id != usuario_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro usuario con el nombre '{usuario_update.username}'"
                )
        
        # Verificar unicidad de email si se está cambiando
        if usuario_update.email and usuario_update.email != db_usuario.email:
            existing = db.query(User).filter(
                User.email == usuario_update.email,
                User.id != usuario_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro usuario con el email '{usuario_update.email}'"
                )
        
        # Actualizar campos
        update_data = usuario_update.model_dump(exclude_unset=True)
        if 'username' in update_data:
            update_data['username'] = update_data['username'].lower()
        
        # Si se proporciona una nueva contraseña, hashearla
        if 'password' in update_data and update_data['password'] is not None and update_data['password'].strip():
            update_data['hashed_password'] = get_password_hash(update_data['password'].strip())
            del update_data['password']  # Eliminar el campo password del diccionario
        
        for field, value in update_data.items():
            setattr(db_usuario, field, value)
        
        db_usuario.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_usuario)
        
        return db_usuario
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el usuario: {str(e)}"
        )


@router.patch("/{usuario_id}/activar", response_model=UserResponse, summary="Activar/Desactivar usuario")
def toggle_usuario_estado(
    usuario_id: int,
    estado: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Cambia el estado de un usuario (activar/desactivar).
    
    **Permisos requeridos**: ADMIN
    
    **Parámetros**:
    - usuario_id: ID del usuario
    - estado: Nuevo estado (True=Activo, False=Inactivo)
    
    **Retorna**: Usuario actualizado
    """
    try:
        db_usuario = db.query(User).filter(User.id == usuario_id).first()
        if not db_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # No permitir desactivar al propio usuario admin
        if usuario_id == current_user.id and not estado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes desactivar tu propia cuenta"
            )
        
        db_usuario.is_active = estado
        db_usuario.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_usuario)
        
        return db_usuario
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar el estado del usuario: {str(e)}"
        )


@router.post("/{usuario_id}/reset-password", summary="Resetear contraseña")
def reset_usuario_password(
    usuario_id: int,
    password_reset: UserPasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Resetea la contraseña de un usuario.
    
    **Permisos requeridos**: ADMIN
    
    **Parámetros**:
    - usuario_id: ID del usuario
    - password_reset: Nueva contraseña
    
    **Retorna**: Mensaje de confirmación
    """
    try:
        db_usuario = db.query(User).filter(User.id == usuario_id).first()
        if not db_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Hashear y actualizar contraseña
        db_usuario.hashed_password = get_password_hash(password_reset.new_password)
        db_usuario.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": f"Contraseña actualizada exitosamente para el usuario '{db_usuario.full_name}'",
            "usuario_id": usuario_id,
            "username": db_usuario.username
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al resetear la contraseña: {str(e)}"
        )


@router.delete("/{usuario_id}", summary="Eliminar usuario")
def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Elimina un usuario del sistema.
    Solo se pueden eliminar usuarios que estén desactivados previamente
    y que no tengan registros relacionados (movimientos de inventario, ventas, órdenes, etc.).
    
    **Permisos requeridos**: ADMIN
    
    **Parámetros**:
    - usuario_id: ID del usuario a eliminar
    
    **Retorna**: Mensaje de confirmación
    """
    try:
        from sqlalchemy import text
        
        # Verificar que el usuario existe y obtener info básica sin relaciones
        result = db.execute(
            text("SELECT id, username, full_name, role, is_active FROM users WHERE id = :user_id"),
            {"user_id": usuario_id}
        )
        usuario_row = result.fetchone()
        
        if not usuario_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # No permitir eliminar al propio usuario
        if usuario_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminar tu propia cuenta"
            )
        
        # Verificar que el usuario esté desactivado
        if usuario_row[4]:  # is_active
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un usuario activo. Debes desactivarlo primero."
            )
        
        # Verificar si el usuario tiene registros relacionados
        relaciones_encontradas = []
        
        # Verificar inventory_movements
        movimientos_count = db.execute(
            text("SELECT COUNT(*) FROM inventory_movements WHERE user_id = :user_id"),
            {"user_id": usuario_id}
        ).scalar()
        if movimientos_count > 0:
            relaciones_encontradas.append(f"{movimientos_count} movimiento(s) de inventario")
        
        # Verificar sales (si existe la tabla)
        try:
            ventas_count = db.execute(
                text("SELECT COUNT(*) FROM sales WHERE user_id = :user_id"),
                {"user_id": usuario_id}
            ).scalar()
            if ventas_count > 0:
                relaciones_encontradas.append(f"{ventas_count} venta(s)")
        except:
            pass  # La tabla puede no existir
        
        # Verificar orders (si existe la tabla)
        try:
            orders_count = db.execute(
                text("SELECT COUNT(*) FROM orders WHERE waiter_id = :user_id OR created_by = :user_id"),
                {"user_id": usuario_id}
            ).scalar()
            if orders_count > 0:
                relaciones_encontradas.append(f"{orders_count} orden(es)")
        except:
            pass  # La tabla puede no existir
        
        # Verificar usuario_permiso (tabla intermedia - esta se puede eliminar automáticamente)
        # Pero mejor verificamos solo las relaciones críticas que no podemos eliminar
        
        # Si hay relaciones, no permitir eliminación
        if relaciones_encontradas:
            relaciones_str = ", ".join(relaciones_encontradas)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el usuario porque tiene registros relacionados: {relaciones_str}. "
                       "Los usuarios con historial en el sistema deben mantenerse para conservar la integridad de los datos."
            )
        
        # Guardar info antes de eliminar
        usuario_info = {
            "id": usuario_row[0],
            "username": usuario_row[1],
            "full_name": usuario_row[2],
            "role": usuario_row[3]
        }
        
        # Eliminar usuario directamente con SQL para evitar cargar relaciones
        db.execute(
            text("DELETE FROM users WHERE id = :user_id"),
            {"user_id": usuario_id}
        )
        db.commit()
        
        return {
            "success": True,
            "message": f"Usuario '{usuario_info['full_name']}' eliminado exitosamente",
            "usuario": usuario_info
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # Si es un error de foreign key, proporcionar un mensaje más claro
        error_str = str(e)
        if "violates foreign key constraint" in error_str or "ForeignKeyViolation" in error_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el usuario porque tiene registros relacionados en el sistema (movimientos de inventario, ventas u órdenes). "
                       "Los usuarios con historial deben mantenerse para conservar la integridad de los datos."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el usuario: {str(e)}"
        )


@router.get("/roles/disponibles", summary="Listar roles disponibles")
def get_roles_disponibles(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la lista de roles disponibles en el sistema.
    
    **Retorna**: Lista de roles con descripciones
    """
    roles = [
        {
            "value": UserRole.ADMIN.value,
            "label": "Administrador",
            "descripcion": "Acceso completo al sistema"
        },
        {
            "value": UserRole.MESERO.value,
            "label": "Mesero",
            "descripcion": "Gestión de pedidos y mesas"
        },
        {
            "value": UserRole.COCINA.value,
            "label": "Cocina",
            "descripcion": "Visualización y gestión de pedidos de cocina"
        },
        {
            "value": UserRole.CAJA.value,
            "label": "Caja",
            "descripcion": "Gestión de pagos y cierre de caja"
        }
    ]
    
    return {
        "roles": roles,
        "total": len(roles)
    }

