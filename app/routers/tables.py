"""
Router para gestión de mesas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User, UserRole
from app.models.location import Table, TableStatus, Location, LocationType
from app.models.order import Order
from app.schemas.location import TableCreate, TableUpdate, TableResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/tables", tags=["mesas"])


@router.get("/", response_model=List[TableResponse])
def get_tables(
    location_id: Optional[int] = None,
    status: Optional[TableStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener lista de mesas"""
    query = db.query(Table)
    
    if location_id:
        query = query.filter(Table.location_id == location_id)
    
    if status:
        query = query.filter(Table.status == status)
    
    # Obtener mesas activas
    query = query.filter(Table.is_active == True)
    
    tables = query.order_by(Table.table_number).offset(skip).limit(limit).all()
    
    # Agregar información de órdenes activas para cada mesa
    for table in tables:
        try:
            active_orders = db.query(Order).filter(
                Order.table_id == table.id,
                Order.status.in_(["pendiente", "en_preparacion", "listo"])
            ).count()
            
            # Agregar como atributo dinámico
            table.active_orders = active_orders
            
            # Si tiene órdenes activas, marcar como ocupada
            if active_orders > 0 and table.status == TableStatus.LIBRE:
                table.status = TableStatus.OCUPADA
                db.commit()
        except Exception as e:
            # Si hay error, establecer en 0
            table.active_orders = 0
    
    return tables


@router.get("/{table_id}", response_model=TableResponse)
def get_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener mesa específica"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    # Agregar información de órdenes activas
    active_orders = db.query(Order).filter(
        Order.table_id == table.id,
        Order.status.in_(["pendiente", "en_preparacion", "listo"])
    ).count()
    
    table.active_orders = active_orders
    
    return table


@router.post("/", response_model=TableResponse)
def create_table(
    table_data: TableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva mesa (admin y meseros)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MESERO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y meseros pueden crear mesas"
        )
    
    # Si no se proporciona location_id, usar la primera ubicación disponible
    if not table_data.location_id:
        location = db.query(Location).first()
        if not location:
            # Crear una ubicación por defecto si no existe ninguna
            location = Location(
                name="Restaurante Principal",
                description="Ubicación principal del restaurante",
                location_type=LocationType.RESTAURANTE
            )
            db.add(location)
            db.commit()
            db.refresh(location)
        table_data.location_id = location.id
    else:
        # Verificar que la ubicación existe
        location = db.query(Location).filter(Location.id == table_data.location_id).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ubicación no encontrada"
            )
    
    # Verificar que el número de mesa no existe en esa ubicación
    existing_table = db.query(Table).filter(
        Table.location_id == table_data.location_id,
        Table.table_number == table_data.table_number
    ).first()
    
    if existing_table:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una mesa con ese número en esta ubicación"
        )
    
    # Crear la mesa
    db_table = Table(**table_data.model_dump())
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    
    return db_table


@router.put("/{table_id}", response_model=TableResponse)
def update_table(
    table_id: int,
    table_update: TableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar mesa"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    # Solo admin puede modificar mesas, meseros solo pueden cambiar estado
    if current_user.role not in [UserRole.ADMIN, UserRole.MESERO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar mesas"
        )
    
    # Si es mesero, solo puede cambiar el estado
    if current_user.role == UserRole.MESERO:
        if table_update.status:
            table.status = table_update.status
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los meseros solo pueden cambiar el estado de la mesa"
            )
    else:
        # Admin puede modificar todo
        update_data = table_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(table, field, value)
    
    db.commit()
    db.refresh(table)
    
    return table


@router.put("/{table_id}/status", response_model=TableResponse)
def update_table_status(
    table_id: int,
    new_status: TableStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar solo el estado de la mesa"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    # Verificar permisos según el nuevo estado
    if new_status == TableStatus.MANTENIMIENTO:
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores y supervisores pueden poner mesas en mantenimiento"
            )
    
    # Verificar que no haya órdenes activas si se quiere liberar
    if new_status == TableStatus.LIBRE:
        active_orders = db.query(Order).filter(
            Order.table_id == table.id,
            Order.status.in_(["pendiente", "en_preparacion", "listo"])
        ).count()
        
        if active_orders > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede liberar una mesa con órdenes activas"
            )
    
    table.status = new_status
    db.commit()
    db.refresh(table)
    
    return table


@router.get("/{table_id}/orders")
def get_table_orders(
    table_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener órdenes de una mesa"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    query = db.query(Order).filter(Order.table_id == table_id)
    
    if active_only:
        query = query.filter(
            Order.status.in_(["pendiente", "en_preparacion", "listo"])
        )
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    return orders


@router.delete("/{table_id}")
def delete_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar mesa (solo admin)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar mesas"
        )
    
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    # Verificar que no tenga órdenes activas
    active_orders = db.query(Order).filter(
        Order.table_id == table.id,
        Order.status.in_(["pendiente", "en_preparacion", "listo"])
    ).count()
    
    if active_orders > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una mesa con órdenes activas"
        )
    
    # Marcar como inactiva en lugar de eliminar físicamente
    table.is_active = False
    db.commit()
    
    return {"message": "Mesa eliminada exitosamente"}
