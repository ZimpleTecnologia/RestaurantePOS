"""
Router para gestión de Mesas
Endpoints CRUD completos para el módulo de mesas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.database import get_db
from app.models.mesa import Mesa
from app.schemas.mesa import (
    MesaCreate, MesaUpdate, MesaResponse, MesaListResponse, MesaActivarDesactivar
)
from app.auth import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/mesas", tags=["Mesas"])


@router.get("/", response_model=MesaListResponse, summary="Listar todas las mesas")
def get_mesas(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    estado: Optional[bool] = Query(None, description="Filtrar por estado (True=Activo, False=Inactivo)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene la lista de todas las mesas del restaurante.
    
    **Permisos requeridos**: Usuario activo
    
    **Parámetros**:
    - skip: Registros a saltar para paginación
    - limit: Máximo de registros a devolver
    - estado: Filtrar por estado (opcional)
    
    **Retorna**: Lista de mesas con total de registros
    """
    try:
        query = db.query(Mesa)
        
        # Filtro opcional por estado
        if estado is not None:
            query = query.filter(Mesa.estado == estado)
        
        total = query.count()
        mesas = query.order_by(Mesa.numero).offset(skip).limit(limit).all()
        
        return MesaListResponse(mesas=mesas, total=total)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las mesas: {str(e)}"
        )


@router.get("/{mesa_id}", response_model=MesaResponse, summary="Obtener una mesa específica")
def get_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene los detalles de una mesa específica por su ID.
    
    **Permisos requeridos**: Usuario activo
    
    **Parámetros**:
    - mesa_id: ID de la mesa
    
    **Retorna**: Datos de la mesa
    """
    mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mesa con ID {mesa_id} no encontrada"
        )
    return mesa


@router.post("/", response_model=MesaResponse, status_code=status.HTTP_201_CREATED, summary="Crear nueva mesa")
def create_mesa(
    mesa: MesaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Crea una nueva mesa en el sistema.
    
    **Permisos requeridos**: ADMIN
    
    **Parámetros**:
    - mesa: Datos de la mesa a crear
    
    **Retorna**: Mesa creada
    """
    try:
        # Verificar que no exista una mesa con el mismo número
        existing_mesa = db.query(Mesa).filter(Mesa.numero == mesa.numero).first()
        if existing_mesa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una mesa con el número {mesa.numero}"
            )
        
        # Crear nueva mesa
        db_mesa = Mesa(**mesa.dict())
        db.add(db_mesa)
        db.commit()
        db.refresh(db_mesa)
        
        return db_mesa
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad: El número de mesa ya existe"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la mesa: {str(e)}"
        )


@router.put("/{mesa_id}", response_model=MesaResponse, summary="Actualizar mesa")
def update_mesa(
    mesa_id: int,
    mesa_update: MesaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Actualiza los datos de una mesa existente.
    
    **Permisos requeridos**: ADMIN
    
    **Parámetros**:
    - mesa_id: ID de la mesa a actualizar
    - mesa_update: Datos a actualizar
    
    **Retorna**: Mesa actualizada
    """
    try:
        # Buscar la mesa
        db_mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        if not db_mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesa con ID {mesa_id} no encontrada"
            )
        
        # Verificar unicidad del número si se está cambiando
        if mesa_update.numero and mesa_update.numero != db_mesa.numero:
            existing = db.query(Mesa).filter(
                Mesa.numero == mesa_update.numero,
                Mesa.id != mesa_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otra mesa con el número {mesa_update.numero}"
                )
        
        # Actualizar campos
        update_data = mesa_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_mesa, field, value)
        
        db_mesa.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_mesa)
        
        return db_mesa
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la mesa: {str(e)}"
        )


@router.patch("/{mesa_id}/activar", response_model=MesaResponse, summary="Activar/Desactivar mesa")
def toggle_mesa_estado(
    mesa_id: int,
    estado_request: MesaActivarDesactivar,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Cambia el estado de una mesa (activar/desactivar).
    
    **Permisos requeridos**: ADMIN
    
    **Parámetros**:
    - mesa_id: ID de la mesa
    - estado_request: Nuevo estado (True=Activo, False=Inactivo)
    
    **Retorna**: Mesa actualizada
    """
    try:
        db_mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        if not db_mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesa con ID {mesa_id} no encontrada"
            )
        
        db_mesa.estado = estado_request.estado
        db_mesa.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_mesa)
        
        return db_mesa
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar el estado de la mesa: {str(e)}"
        )


@router.delete("/{mesa_id}", status_code=status.HTTP_200_OK, summary="Eliminar mesa")
def delete_mesa(
    mesa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Elimina una mesa del sistema.
    
    **Permisos requeridos**: ADMIN
    
    **Parámetros**:
    - mesa_id: ID de la mesa a eliminar
    
    **Retorna**: Mensaje de confirmación
    """
    try:
        db_mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        if not db_mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesa con ID {mesa_id} no encontrada"
            )
        
        # Verificar si la mesa tiene pedidos asociados (si aplica en el futuro)
        # Aquí puedes agregar lógica para verificar relaciones
        
        # Guardar info antes de eliminar
        mesa_info = {
            "id": db_mesa.id,
            "numero": db_mesa.numero,
            "nombre": db_mesa.nombre
        }
        
        db.delete(db_mesa)
        db.commit()
        
        return {
            "success": True,
            "message": f"Mesa '{mesa_info['nombre']}' (#{mesa_info['numero']}) eliminada exitosamente",
            "mesa": mesa_info
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la mesa: {str(e)}"
        )

