"""
Router de productos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user, require_admin
from app.models.product import Product, Category, SubCategory
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductWithCategory,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse
)

router = APIRouter(prefix="/products", tags=["productos"])


# Rutas para categorías
@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de categorías"""
    categories = db.query(Category).filter(Category.is_active == True).offset(skip).limit(limit).all()
    return categories


@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crear nueva categoría"""
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Obtener categoría por ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualizar categoría"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    for field, value in category.dict(exclude_unset=True).items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


# Rutas para subcategorías
@router.get("/subcategories", response_model=List[SubCategoryResponse])
def get_subcategories(
    category_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de subcategorías"""
    query = db.query(SubCategory).filter(SubCategory.is_active == True)
    if category_id:
        query = query.filter(SubCategory.category_id == category_id)
    subcategories = query.offset(skip).limit(limit).all()
    return subcategories


@router.post("/subcategories", response_model=SubCategoryResponse)
def create_subcategory(
    subcategory: SubCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crear nueva subcategoría"""
    db_subcategory = SubCategory(**subcategory.dict())
    db.add(db_subcategory)
    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory


# Rutas para productos
@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtener lista de productos"""
    query = db.query(Product).filter(Product.is_active == True)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.code.ilike(f"%{search}%"))
        )
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nuevo producto"""
    # Verificar si el código ya existe
    existing_product = db.query(Product).filter(Product.code == product.code).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de producto ya existe"
        )
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtener producto por ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar producto"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    for field, value in product.dict(exclude_unset=True).items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eliminar producto (desactivar)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db_product.is_active = False
    db.commit()
    return {"message": "Producto eliminado exitosamente"}


# Reportes de inventario
@router.get("/reports/inventory")
def get_inventory_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener reporte de inventario"""
    from sqlalchemy import func
    
    # Productos con stock bajo
    low_stock_products = db.query(Product).filter(
        Product.stock <= Product.min_stock,
        Product.is_active == True
    ).all()
    
    # Productos sin stock
    out_of_stock_products = db.query(Product).filter(
        Product.stock == 0,
        Product.is_active == True
    ).all()
    
    # Productos por categoría
    products_by_category = db.query(
        Category.name,
        func.count(Product.id).label('total_products'),
        func.sum(Product.stock).label('total_stock'),
        func.sum(Product.stock * Product.price).label('total_value')
    ).join(Product, Category.id == Product.category_id)\
     .filter(Product.is_active == True)\
     .group_by(Category.name).all()
    
    # Valor total del inventario
    total_inventory_value = db.query(func.sum(Product.stock * Product.price))\
        .filter(Product.is_active == True).scalar() or 0
    
    return {
        "total_products": db.query(Product).filter(Product.is_active == True).count(),
        "low_stock_count": len(low_stock_products),
        "out_of_stock_count": len(out_of_stock_products),
        "total_inventory_value": float(total_inventory_value),
        "low_stock_products": [
            {
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "stock": p.stock,
                "min_stock": p.min_stock
            }
            for p in low_stock_products[:10]  # Top 10
        ],
        "out_of_stock_products": [
            {
                "id": p.id,
                "name": p.name,
                "code": p.code
            }
            for p in out_of_stock_products[:10]  # Top 10
        ],
        "products_by_category": [
            {
                "category": item.name,
                "total_products": item.total_products,
                "total_stock": item.total_stock or 0,
                "total_value": float(item.total_value or 0)
            }
            for item in products_by_category
        ]
    } 