"""
Router para el manejo de mesas del restaurante
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.auth import get_current_active_user
from app.services.table_service import TableService
from app.models.location import TableStatus

router = APIRouter(prefix="/tables", tags=["tables"])


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class TableCreate(BaseModel):
    table_number: str
    name: str
    capacity: int = 4
    location: Optional[str] = None
    description: Optional[str] = None

class TableUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TableStatus] = None

class TableResponse(BaseModel):
    id: int
    table_number: str
    name: str
    capacity: int
    status: TableStatus
    location: Optional[str] = None
    description: Optional[str] = None
    is_available: bool
    has_active_order: bool

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS DE MESAS
# ============================================================================

@router.get("/", response_model=List[TableResponse])
def get_all_tables(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener todas las mesas"""
    tables = TableService.get_all_tables(db)
    return tables

@router.get("/available", response_model=List[TableResponse])
def get_available_tables(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener mesas disponibles"""
    tables = TableService.get_available_tables(db)
    return tables

@router.get("/occupied", response_model=List[TableResponse])
def get_occupied_tables(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener mesas ocupadas"""
    tables = TableService.get_occupied_tables(db)
    return tables

@router.get("/{table_id}", response_model=TableResponse)
def get_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener mesa específica"""
    table = TableService.get_table_by_id(db, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    return table

@router.post("/", response_model=TableResponse)
def create_table(
    table_data: TableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear una nueva mesa"""
    # Verificar que el número de mesa no exista
    existing_table = TableService.get_table_by_number(db, table_data.table_number)
    if existing_table:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una mesa con ese número"
        )
    
    table = TableService.create_table(
        db=db,
        table_number=table_data.table_number,
        name=table_data.name,
        capacity=table_data.capacity,
        location=table_data.location,
        description=table_data.description
    )
    return table

@router.put("/{table_id}", response_model=TableResponse)
def update_table(
    table_id: int,
    table_data: TableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar mesa"""
    table = TableService.get_table_by_id(db, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    # Actualizar campos
    if table_data.name is not None:
        table.name = table_data.name
    if table_data.capacity is not None:
        table.capacity = table_data.capacity
    if table_data.location is not None:
        table.location = table_data.location
    if table_data.description is not None:
        table.description = table_data.description
    if table_data.status is not None:
        table.status = table_data.status
    
    db.commit()
    db.refresh(table)
    return table

@router.post("/{table_id}/occupy")
def occupy_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Ocupar una mesa"""
    table = TableService.occupy_table(db, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    return {
        "message": f"Mesa {table.name} ocupada exitosamente",
        "table": {
            "id": table.id,
            "table_number": table.table_number,
            "name": table.name,
            "status": table.status
        }
    }

@router.post("/{table_id}/free")
def free_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Liberar una mesa"""
    table = TableService.free_table(db, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    
    return {
        "message": f"Mesa {table.name} liberada exitosamente",
        "table": {
            "id": table.id,
            "table_number": table.table_number,
            "name": table.name,
            "status": table.status
        }
    }

@router.get("/{table_id}/with-order")
def get_table_with_order(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener mesa con su pedido activo"""
    table_data = TableService.get_table_with_active_order(db, table_id)
    if not table_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada"
        )
    return table_data

@router.get("/status/summary")
def get_tables_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener resumen del estado de las mesas"""
    summary = TableService.get_table_status_summary(db)
    return summary

@router.post("/initialize")
def initialize_default_tables(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Inicializar mesas por defecto"""
    created_tables = TableService.initialize_default_tables(db)
    return {
        "message": f"Se crearon {len(created_tables)} mesas por defecto",
        "tables": [
            {
                "id": table.id,
                "table_number": table.table_number,
                "name": table.name,
                "capacity": table.capacity,
                "location": table.location
            }
            for table in created_tables
        ]
    }
