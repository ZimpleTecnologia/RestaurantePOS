"""
Router de inventario
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.inventory import InventoryMovement
from app.auth.dependencies import get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/inventory", tags=["inventario"])


class StockAdjustmentCreate(BaseModel):
    """Esquema para ajuste de stock"""
    product_id: int
    adjustment_type: str  # 'add', 'subtract', 'set'
    quantity: int
    new_stock: int
    reason: str
    notes: str = ""


class InventoryMovementResponse(BaseModel):
    """Esquema de respuesta para movimiento de inventario"""
    id: int
    product_id: int
    adjustment_type: str
    quantity: int
    previous_stock: int
    new_stock: int
    reason: str
    notes: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/adjust")
def adjust_stock(
    adjustment: StockAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Ajustar stock de un producto"""
    # Verificar que el producto existe
    product = db.query(Product).filter(Product.id == adjustment.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar que el stock no sea negativo
    if adjustment.new_stock < 0:
        raise HTTPException(status_code=400, detail="El stock no puede ser negativo")
    
    # Guardar stock anterior
    previous_stock = product.stock
    
    # Actualizar stock del producto
    product.stock = adjustment.new_stock
    
    # Crear movimiento de inventario
    movement = InventoryMovement(
        product_id=adjustment.product_id,
        adjustment_type=adjustment.adjustment_type,
        quantity=adjustment.quantity,
        previous_stock=previous_stock,
        new_stock=adjustment.new_stock,
        reason=adjustment.reason,
        notes=adjustment.notes,
        user_id=current_user.id
    )
    
    db.add(movement)
    db.commit()
    
    return {"message": "Stock ajustado correctamente"}


@router.get("/movements/{product_id}", response_model=List[InventoryMovementResponse])
def get_product_movements(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener movimientos de inventario de un producto"""
    # Verificar que el producto existe
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    movements = db.query(InventoryMovement).filter(
        InventoryMovement.product_id == product_id
    ).order_by(InventoryMovement.created_at.desc()).all()
    
    return movements
