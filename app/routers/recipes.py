"""
Router para gestión de recetas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.user import User, UserRole
from app.models.product import Product, ProductType
from app.models.recipe import Recipe, RecipeItem
from app.schemas.recipe import (
    RecipeCreate, RecipeUpdate, RecipeResponse, RecipeWithItems,
    RecipeItemCreate, RecipeItemUpdate, RecipeItemResponse,
    RecipeCostCalculation, InventoryConsumptionRequest, 
    InventoryConsumptionResponse, InventoryAvailabilityCheck,
    InventoryAvailabilityResponse
)
from app.auth.dependencies import get_current_active_user
from app.services.inventory_consumption_service import InventoryConsumptionService

router = APIRouter(prefix="/recipes", tags=["recetas"])


def get_inventory_consumption_service(db: Session = Depends(get_db)) -> InventoryConsumptionService:
    """Dependency para obtener el servicio de consumo de inventario"""
    return InventoryConsumptionService(db)


# ==================== ENDPOINTS DE RECETAS ====================

@router.post("/", response_model=RecipeResponse)
def create_recipe(
    recipe_data: RecipeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crear nueva receta"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear recetas"
        )
    
    # Verificar que el producto existe y es de tipo venta
    product = db.query(Product).filter(Product.id == recipe_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    if not product.is_sales_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden crear recetas para productos de venta"
        )
    
    # Verificar que no existe ya una receta activa para este producto
    existing_recipe = db.query(Recipe).filter(
        and_(
            Recipe.product_id == recipe_data.product_id,
            Recipe.is_active == True
        )
    ).first()
    
    if existing_recipe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una receta activa para este producto"
        )
    
    # Crear la receta
    recipe = Recipe(
        name=recipe_data.name,
        description=recipe_data.description,
        product_id=recipe_data.product_id,
        preparation_time=recipe_data.preparation_time,
        instructions=recipe_data.instructions,
        notes=recipe_data.notes
    )
    
    db.add(recipe)
    db.flush()  # Para obtener el ID de la receta
    
    # Crear los items de la receta
    for item_data in recipe_data.items:
        # Verificar que el ingrediente existe y es de tipo inventario
        ingredient = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingrediente con ID {item_data.product_id} no encontrado"
            )
        
        if not ingredient.is_inventory_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El producto {ingredient.name} no es una materia prima"
            )
        
        recipe_item = RecipeItem(
            recipe_id=recipe.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit=item_data.unit,
            is_optional=item_data.is_optional,
            notes=item_data.notes
        )
        
        db.add(recipe_item)
    
    db.commit()
    db.refresh(recipe)
    
    return recipe


@router.get("/", response_model=List[RecipeResponse])
def get_recipes(
    active_only: bool = Query(True, description="Solo recetas activas"),
    product_id: Optional[int] = Query(None, description="Filtrar por producto"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de recetas"""
    query = db.query(Recipe)
    
    if active_only:
        query = query.filter(Recipe.is_active == True)
    
    if product_id:
        query = query.filter(Recipe.product_id == product_id)
    
    recipes = query.all()
    return recipes


@router.get("/{recipe_id}", response_model=RecipeWithItems)
def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener receta por ID con sus ingredientes"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada"
        )
    
    return recipe


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar receta"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar recetas"
        )
    
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada"
        )
    
    # Actualizar campos
    for field, value in recipe_data.dict(exclude_unset=True).items():
        setattr(recipe, field, value)
    
    db.commit()
    db.refresh(recipe)
    
    return recipe


@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar receta (desactivar)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar recetas"
        )
    
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada"
        )
    
    recipe.is_active = False
    db.commit()
    
    return {"message": "Receta eliminada exitosamente"}


# ==================== ENDPOINTS DE ITEMS DE RECETA ====================

@router.post("/{recipe_id}/items", response_model=RecipeItemResponse)
def add_recipe_item(
    recipe_id: int,
    item_data: RecipeItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Agregar ingrediente a una receta"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar recetas"
        )
    
    # Verificar que la receta existe
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada"
        )
    
    # Verificar que el ingrediente existe y es de tipo inventario
    ingredient = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente no encontrado"
        )
    
    if not ingredient.is_inventory_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El producto no es una materia prima"
        )
    
    # Verificar que no existe ya este ingrediente en la receta
    existing_item = db.query(RecipeItem).filter(
        and_(
            RecipeItem.recipe_id == recipe_id,
            RecipeItem.product_id == item_data.product_id
        )
    ).first()
    
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este ingrediente ya está en la receta"
        )
    
    # Crear el item de receta
    recipe_item = RecipeItem(
        recipe_id=recipe_id,
        product_id=item_data.product_id,
        quantity=item_data.quantity,
        unit=item_data.unit,
        is_optional=item_data.is_optional,
        notes=item_data.notes
    )
    
    db.add(recipe_item)
    db.commit()
    db.refresh(recipe_item)
    
    return recipe_item


@router.put("/items/{item_id}", response_model=RecipeItemResponse)
def update_recipe_item(
    item_id: int,
    item_data: RecipeItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Actualizar ingrediente de receta"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar recetas"
        )
    
    recipe_item = db.query(RecipeItem).filter(RecipeItem.id == item_id).first()
    if not recipe_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de receta no encontrado"
        )
    
    # Actualizar campos
    for field, value in item_data.dict(exclude_unset=True).items():
        setattr(recipe_item, field, value)
    
    db.commit()
    db.refresh(recipe_item)
    
    return recipe_item


@router.delete("/items/{item_id}")
def delete_recipe_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Eliminar ingrediente de receta"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar recetas"
        )
    
    recipe_item = db.query(RecipeItem).filter(RecipeItem.id == item_id).first()
    if not recipe_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de receta no encontrado"
        )
    
    db.delete(recipe_item)
    db.commit()
    
    return {"message": "Ingrediente eliminado de la receta exitosamente"}


# ==================== ENDPOINTS DE CÁLCULO DE COSTOS ====================

@router.get("/{recipe_id}/cost", response_model=RecipeCostCalculation)
def calculate_recipe_cost(
    recipe_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    consumption_service: InventoryConsumptionService = Depends(get_inventory_consumption_service)
):
    """Calcular el costo actual de una receta"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receta no encontrada"
        )
    
    cost_info = consumption_service.get_recipe_cost(recipe.product_id)
    
    return RecipeCostCalculation(
        recipe_id=recipe_id,
        total_cost=cost_info["total_cost"],
        ingredients=cost_info["ingredients"],
        last_updated=recipe.updated_at or recipe.created_at
    )


# ==================== ENDPOINTS DE CONSUMO DE INVENTARIO ====================

@router.post("/check-availability", response_model=InventoryAvailabilityResponse)
def check_inventory_availability(
    request: InventoryAvailabilityCheck,
    current_user: User = Depends(get_current_active_user),
    consumption_service: InventoryConsumptionService = Depends(get_inventory_consumption_service)
):
    """Verificar disponibilidad de inventario para un producto"""
    try:
        availability = consumption_service.check_inventory_availability(
            request.product_id, 
            request.quantity
        )
        return InventoryAvailabilityResponse(**availability)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/consume-inventory", response_model=InventoryConsumptionResponse)
def consume_inventory(
    request: InventoryConsumptionRequest,
    current_user: User = Depends(get_current_active_user),
    consumption_service: InventoryConsumptionService = Depends(get_inventory_consumption_service)
):
    """Consumir inventario al vender un producto"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.CAJA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para consumir inventario"
        )
    
    try:
        result = consumption_service.consume_inventory_for_sale(
            request.product_id,
            request.quantity,
            current_user.id,
            request.sale_id
        )
        return InventoryConsumptionResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== ENDPOINTS DE PRODUCTOS ====================

@router.get("/products/with-recipes", response_model=List[dict])
def get_products_with_recipes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener productos de venta que tienen recetas"""
    products = db.query(Product).filter(
        and_(
            Product.product_type == ProductType.SALES,
            Product.is_active == True
        )
    ).all()
    
    result = []
    for product in products:
        recipe = db.query(Recipe).filter(
            and_(
                Recipe.product_id == product.id,
                Recipe.is_active == True
            )
        ).first()
        
        result.append({
            "id": product.id,
            "name": product.name,
            "code": product.code,
            "price": float(product.price),
            "has_recipe": recipe is not None,
            "recipe_id": recipe.id if recipe else None,
            "recipe_name": recipe.name if recipe else None,
            "preparation_time": recipe.preparation_time if recipe else 0
        })
    
    return result


@router.get("/products/inventory", response_model=List[dict])
def get_inventory_products(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtener productos de inventario (materias primas)"""
    products = db.query(Product).filter(
        and_(
            Product.product_type == ProductType.INVENTORY,
            Product.is_active == True
        )
    ).all()
    
    return [
        {
            "id": product.id,
            "name": product.name,
            "code": product.code,
            "stock_quantity": product.stock_quantity,
            "min_stock_level": product.min_stock_level,
            "purchase_price": float(product.purchase_price or 0),
            "unit": product.unit,
            "supplier_name": product.supplier.name if product.supplier else None
        }
        for product in products
    ]
