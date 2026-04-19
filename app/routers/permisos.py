"""
Router para gestión de Permisos
Endpoints para manejo de permisos y asignación a usuarios
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.database import get_db
from app.models.permiso import Permiso
from app.models.user import User
from app.schemas.permiso import (
    PermisoCreate, PermisoUpdate, PermisoResponse, PermisoListResponse,
    AsignarPermisoRequest, RemoverPermisoRequest, PermisoSimple
)
from app.auth import get_current_active_user, require_admin

router = APIRouter(prefix="/permisos", tags=["Permisos"])


# ============================================================================
# CRUD DE PERMISOS
# ============================================================================

@router.get("/", response_model=PermisoListResponse, summary="Listar todos los permisos")
def get_permisos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    modulo: Optional[str] = Query(None, description="Filtrar por módulo"),
    estado: Optional[bool] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la lista de todos los permisos del sistema.
    
    **Permisos requeridos**: Usuario activo
    
    **Retorna**: Lista de permisos
    """
    try:
        query = db.query(Permiso)
        
        if modulo:
            query = query.filter(Permiso.modulo == modulo.lower())
        if estado is not None:
            query = query.filter(Permiso.estado == estado)
        
        total = query.count()
        permisos = query.order_by(Permiso.modulo, Permiso.nombre).offset(skip).limit(limit).all()
        
        return PermisoListResponse(permisos=permisos, total=total)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener permisos: {str(e)}"
        )


@router.get("/{permiso_id}", response_model=PermisoResponse, summary="Obtener un permiso específico")
def get_permiso(
    permiso_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene un permiso por ID"""
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    if not permiso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permiso con ID {permiso_id} no encontrado"
        )
    return permiso


@router.post("/", response_model=PermisoResponse, status_code=status.HTTP_201_CREATED, summary="Crear nuevo permiso")
def create_permiso(
    permiso: PermisoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Crea un nuevo permiso en el sistema.
    
    **Permisos requeridos**: ADMIN
    """
    try:
        # Verificar que no exista un permiso con el mismo código
        existing = db.query(Permiso).filter(Permiso.codigo == permiso.codigo).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un permiso con el código '{permiso.codigo}'"
            )
        
        db_permiso = Permiso(**permiso.dict())
        db.add(db_permiso)
        db.commit()
        db.refresh(db_permiso)
        
        return db_permiso
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad: El código de permiso ya existe"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el permiso: {str(e)}"
        )


@router.put("/{permiso_id}", response_model=PermisoResponse, summary="Actualizar permiso")
def update_permiso(
    permiso_id: int,
    permiso_update: PermisoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza un permiso existente"""
    try:
        db_permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
        if not db_permiso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permiso con ID {permiso_id} no encontrado"
            )
        
        # Verificar unicidad del código si se está cambiando
        if permiso_update.codigo and permiso_update.codigo != db_permiso.codigo:
            existing = db.query(Permiso).filter(
                Permiso.codigo == permiso_update.codigo,
                Permiso.id != permiso_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro permiso con el código '{permiso_update.codigo}'"
                )
        
        # Actualizar campos
        update_data = permiso_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_permiso, field, value)
        
        db_permiso.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_permiso)
        
        return db_permiso
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el permiso: {str(e)}"
        )


@router.delete("/{permiso_id}", summary="Eliminar permiso")
def delete_permiso(
    permiso_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Elimina un permiso del sistema"""
    try:
        db_permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
        if not db_permiso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permiso con ID {permiso_id} no encontrado"
            )
        
        permiso_info = {
            "id": db_permiso.id,
            "codigo": db_permiso.codigo,
            "nombre": db_permiso.nombre
        }
        
        db.delete(db_permiso)
        db.commit()
        
        return {
            "success": True,
            "message": f"Permiso '{permiso_info['nombre']}' eliminado exitosamente",
            "permiso": permiso_info
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el permiso: {str(e)}"
        )


# ============================================================================
# ASIGNACIÓN DE PERMISOS A USUARIOS
# ============================================================================

@router.get("/usuario/{usuario_id}", response_model=List[PermisoSimple], summary="Obtener permisos de un usuario")
def get_usuario_permisos(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene todos los permisos asignados a un usuario específico.
    
    **Permisos requeridos**: Usuario activo (puede ver sus propios permisos o cualquiera si es ADMIN)
    """
    # Verificar que el usuario existe
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Solo admin puede ver permisos de otros usuarios
    if current_user.id != usuario_id and current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los permisos de otros usuarios"
        )
    
    return usuario.permisos


@router.post("/usuario/{usuario_id}/asignar", summary="Asignar permisos a un usuario")
def asignar_permisos(
    usuario_id: int,
    request: AsignarPermisoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Asigna uno o más permisos a un usuario.
    
    **Permisos requeridos**: ADMIN
    
    **Nota**: Esta operación es incremental, no reemplaza los permisos existentes.
    """
    try:
        # Verificar que el usuario existe
        usuario = db.query(User).filter(User.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Obtener permisos a asignar
        permisos_a_asignar = db.query(Permiso).filter(
            Permiso.id.in_(request.permiso_ids),
            Permiso.estado == True
        ).all()
        
        if len(permisos_a_asignar) != len(request.permiso_ids):
            permisos_encontrados = {p.id for p in permisos_a_asignar}
            permisos_no_encontrados = set(request.permiso_ids) - permisos_encontrados
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Los siguientes IDs de permisos no existen o están inactivos: {permisos_no_encontrados}"
            )
        
        # Asignar permisos (evitar duplicados)
        permisos_actuales = {p.id for p in usuario.permisos}
        permisos_nuevos = []
        
        for permiso in permisos_a_asignar:
            if permiso.id not in permisos_actuales:
                usuario.permisos.append(permiso)
                permisos_nuevos.append(permiso.nombre)
        
        db.commit()
        db.refresh(usuario)
        
        return {
            "success": True,
            "message": f"Permisos asignados exitosamente al usuario '{usuario.full_name}'",
            "usuario_id": usuario_id,
            "permisos_asignados": permisos_nuevos,
            "total_permisos": len(usuario.permisos)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al asignar permisos: {str(e)}"
        )


@router.delete("/usuario/{usuario_id}/remover/{permiso_id}", summary="Remover permiso de un usuario")
def remover_permiso(
    usuario_id: int,
    permiso_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Remueve un permiso específico de un usuario.
    
    **Permisos requeridos**: ADMIN
    """
    try:
        # Verificar que el usuario existe
        usuario = db.query(User).filter(User.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Verificar que el permiso existe
        permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
        if not permiso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permiso con ID {permiso_id} no encontrado"
            )
        
        # Verificar que el usuario tiene ese permiso
        if permiso not in usuario.permisos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El usuario no tiene el permiso '{permiso.nombre}' asignado"
            )
        
        # Remover permiso
        usuario.permisos.remove(permiso)
        db.commit()
        
        return {
            "success": True,
            "message": f"Permiso '{permiso.nombre}' removido del usuario '{usuario.full_name}'",
            "usuario_id": usuario_id,
            "permiso_removido": permiso.nombre
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al remover permiso: {str(e)}"
        )


@router.get("/modulos/", summary="Listar módulos disponibles")
def get_modulos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la lista de módulos únicos en el sistema.
    
    **Retorna**: Lista de módulos con cantidad de permisos por módulo
    """
    try:
        # Consulta SQL para obtener módulos únicos con conteo
        from sqlalchemy import func
        
        modulos = db.query(
            Permiso.modulo,
            func.count(Permiso.id).label('total_permisos')
        ).group_by(Permiso.modulo).all()
        
        return {
            "modulos": [
                {
                    "modulo": modulo,
                    "total_permisos": total
                }
                for modulo, total in modulos
            ],
            "total_modulos": len(modulos)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener módulos: {str(e)}"
        )

