"""
Router de productos
"""
import os
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import xlsxwriter
from io import BytesIO
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.product import Product, Category, SubCategory, ProductType
from app.models.inventory import InventoryMovement
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, InventoryProductResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse
)
from app.auth import get_current_active_user, require_admin

router = APIRouter(prefix="/products", tags=["productos"])

# ==================== ENDPOINTS ESPECÍFICOS POR TIPO (DEBEN IR ANTES QUE LAS RUTAS GENÉRICAS) ====================

@router.get("/inventory")
def get_inventory_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obtener productos de inventario (materias primas) - versión debug"""
    try:
        # Primero probemos sin filtros
        print("🔍 Iniciando consulta de productos...")
        
        # Consulta simple sin filtros
        all_products = db.query(Product).limit(5).all()
        print(f"📊 Total productos encontrados: {len(all_products)}")
        
        # Verificar tipos de product_type
        for product in all_products:
            print(f"  - ID: {product.id}, Nombre: {product.name}, Tipo: {product.product_type}, Tipo Python: {type(product.product_type)}")
        
        # Ahora probemos con filtro de string
        products = db.query(Product).filter(
            Product.is_active == True,
            Product.product_type == "INVENTORY"  # Usar string directamente
        ).offset(skip).limit(limit).all()
        
        print(f"📦 Productos de inventario encontrados: {len(products)}")
        
        # Convertir los productos a diccionarios simples
        result = []
        for product in products:
            product_dict = {
                "id": product.id,
                "name": product.name,
                "code": product.code,
                "description": product.description,
                "product_type": "inventory",
                "category_id": product.category_id,
                "stock_quantity": product.stock_quantity or 0,
                "min_stock_level": product.min_stock_level or 0,
                "max_stock_level": product.max_stock_level or 100,
                "stock": product.stock or 0,
                "min_stock": product.min_stock or 0,
                "max_stock": product.max_stock or 100,
                "unit": product.unit or "unidad",
                "purchase_price": float(product.purchase_price) if product.purchase_price else None,
                "supplier_id": product.supplier_id,
                "supplier": product.supplier,
                "barcode": product.barcode,
                "is_active": bool(product.is_active),
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            }
            result.append(product_dict)
        
        return {
            "success": True,
            "count": len(result),
            "products": result
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error completo: {error_details}")
        return {
            "error": str(e), 
            "type": str(type(e)),
            "details": error_details
        }

@router.get("/sales", response_model=List[ProductResponse])
def get_sales_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obtener productos de venta (platos preparados)"""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.SALES
    ).offset(skip).limit(limit).all()
    return products

@router.get("/inventory/low-stock", response_model=List[InventoryProductResponse])
def get_inventory_low_stock(
    db: Session = Depends(get_db)
):
    """Obtener productos de inventario con stock bajo"""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.INVENTORY,
        Product.stock_quantity <= Product.min_stock_level
    ).all()
    return products

@router.get("/inventory/statistics")
def get_inventory_statistics(db: Session = Depends(get_db)):
    """Obtener estadísticas de inventario"""
    total_products = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.INVENTORY
    ).count()
    
    low_stock = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.INVENTORY,
        Product.stock_quantity <= Product.min_stock_level
    ).count()
    
    out_of_stock = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.INVENTORY,
        Product.stock_quantity == 0
    ).count()
    
    # Calcular valor total del inventario
    total_value = db.query(func.sum(Product.stock_quantity * Product.purchase_price)).filter(
        Product.is_active == True,
        Product.product_type == ProductType.INVENTORY
    ).scalar() or 0
    
    return {
        "total_products": total_products,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "total_value": float(total_value)
    }

@router.get("/sales/statistics")
def get_sales_statistics(db: Session = Depends(get_db)):
    """Obtener estadísticas de productos de venta"""
    total_products = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.SALES
    ).count()
    
    return {
        "total_products": total_products
    }

# Configuración para imágenes
UPLOAD_DIR = "uploads/products"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def generate_product_code() -> str:
    """Generar código único para producto"""
    import time
    timestamp = int(time.time() * 1000) % 1000000  # Últimos 6 dígitos del timestamp
    random_part = uuid.uuid4().hex[:3].upper()  # 3 caracteres aleatorios
    return f"PROD{timestamp:06d}{random_part}"

def save_product_image(file: UploadFile) -> str:
    """Guardar imagen de producto y retornar URL"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    # Generar nombre único para el archivo
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Guardar archivo
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(status_code=400, detail="La imagen debe ser menor a 5MB")
        buffer.write(content)
    
    return f"/uploads/products/{filename}"

# Rutas para categorías
@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Obtener todas las categorías (activas e inactivas)"""
    return db.query(Category).all()

@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Obtener categoría por ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category

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

@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Eliminar categoría (desactivar)"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar si la categoría tiene productos
    products_count = db.query(Product).filter(Product.category_id == category_id).count()
    if products_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la categoría porque tiene {products_count} productos asignados"
        )
    
    # Desactivar la categoría en lugar de eliminarla físicamente
    db_category.is_active = False
    db.commit()
    
    return {"message": "Categoría eliminada exitosamente"}

# Rutas para subcategorías
@router.get("/subcategories", response_model=List[SubCategoryResponse])
def get_subcategories(db: Session = Depends(get_db)):
    """Obtener todas las subcategorías"""
    return db.query(SubCategory).filter(SubCategory.is_active == True).all()

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
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    product_type: Optional[ProductType] = Query(None, description="Filtrar por tipo de producto"),
    db: Session = Depends(get_db)
):
    """Obtener lista de productos"""
    query = db.query(Product).filter(Product.is_active == True)
    
    if product_type:
        query = query.filter(Product.product_type == product_type)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.post("/debug")
async def debug_create_product(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint de debug para crear productos"""
    try:
        print("🔍 Datos recibidos:", data)
        
        # Intentar crear el objeto ProductCreate
        try:
            product = ProductCreate(**data)
            print("✅ ProductCreate válido:", product.dict())
        except Exception as e:
            print("❌ Error en ProductCreate:", str(e))
            return {"error": f"Error en ProductCreate: {str(e)}", "data": data}
        
        # Crear el producto en la base de datos
        code = product.code or generate_product_code()
        
        # Verificar si el código ya existe
        existing_product = db.query(Product).filter(Product.code == code).first()
        if existing_product:
            code = generate_product_code()
        
        # Crear producto
        product_data = {
            "code": code,
            "name": product.name,
            "price": product.price,
            "cost_price": product.cost_price or 0,
            "stock": product.stock_quantity or product.stock or 0,
            "min_stock": product.min_stock_level or product.min_stock or 0,
            "max_stock": product.max_stock or 100,
            "stock_quantity": product.stock_quantity or product.stock or 0,
            "min_stock_level": product.min_stock_level or product.min_stock or 0,
            "unit": product.unit or "unidad",
            "category_id": product.category_id,
            "product_type": product.product_type,
            "purchase_price": product.purchase_price,
            "supplier_id": product.supplier_id,
            "supplier": product.supplier,  # Agregar campo supplier
            "description": product.description,
            "is_active": product.is_active,
            "image_url": None
        }
        
        db_product = Product(**product_data)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        # Crear movimiento de inventario si el producto tiene stock inicial
        if db_product.stock_quantity and db_product.stock_quantity > 0:
            movement = InventoryMovement(
                product_id=db_product.id,
                user_id=current_user.id,
                adjustment_type="entrada",
                reason="Creación de producto con stock inicial",
                quantity=db_product.stock_quantity,
                previous_stock=0,
                new_stock=db_product.stock_quantity,
                notes=f"Producto creado con stock inicial de {db_product.stock_quantity} {db_product.unit or 'unidades'}"
            )
            db.add(movement)
            db.commit()
            print("✅ Movimiento de inventario creado para producto:", db_product.id)
        
        print("✅ Producto creado exitosamente:", db_product.id)
        return {"success": True, "product": db_product, "message": "Producto creado exitosamente"}
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error completo: {error_details}")
        return {"error": str(e), "details": error_details}

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crear nuevo producto con código automático"""
    # Generar código automático si no se proporciona
    code = product.code or generate_product_code()
    
    # Verificar si el código ya existe (muy improbable pero por seguridad)
    existing_product = db.query(Product).filter(Product.code == code).first()
    if existing_product:
        # Generar nuevo código si hay conflicto
        code = generate_product_code()
    
    # Crear producto
    product_data = {
        "code": code,
        "name": product.name,
        "price": product.price,
        "cost_price": product.cost_price or 0,
        "stock": product.stock or 0,
        "min_stock": product.min_stock or 0,
        "max_stock": product.max_stock or 100,
        "category_id": product.category_id,
        "product_type": product.product_type,
        "purchase_price": product.purchase_price,
        "supplier_id": product.supplier_id,
        "supplier": product.supplier,  # Agregar campo supplier
        "description": product.description,
        "is_active": product.is_active,
        "image_url": None  # Por ahora sin imagen
    }
    
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Crear movimiento de inventario si el producto tiene stock inicial
    if db_product.stock_quantity and db_product.stock_quantity > 0:
        movement = InventoryMovement(
            product_id=db_product.id,
            user_id=current_user.id,
            adjustment_type="entrada",
            reason="Creación de producto con stock inicial",
            quantity=db_product.stock_quantity,
            previous_stock=0,
            new_stock=db_product.stock_quantity,
            notes=f"Producto creado con stock inicial de {db_product.stock_quantity} {db_product.unit or 'unidades'}"
        )
        db.add(movement)
        db.commit()
    
    return db_product

# Estadísticas de productos
@router.get("/statistics")
def get_product_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estadísticas de productos"""
    # Total de productos
    total_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Productos activos
    active_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Productos con stock bajo
    low_stock_products = db.query(Product).filter(
        Product.stock_quantity <= Product.min_stock_level,
        Product.is_active == True
    ).count()
    
    # Valor total del inventario
    total_value = db.query(func.sum(Product.stock_quantity * Product.price))\
        .filter(Product.is_active == True).scalar() or 0
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "low_stock_products": low_stock_products,
        "total_value": float(total_value)
    }

# Importar productos desde Excel
@router.post("/import")
def import_products(
    products: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Importar productos desde Excel"""
    imported_count = 0
    errors = []
    
    for i, product_data in enumerate(products.get("products", [])):
        try:
            # Validar datos requeridos
            if not product_data.get("name") or not product_data.get("price"):
                errors.append(f"Fila {i+1}: Nombre y precio son requeridos")
                continue
            
            # Generar código automático
            code = generate_product_code()
            
            # Crear producto
            product = Product(
                code=code,
                name=product_data["name"],
                price=float(product_data["price"]),
                cost_price=float(product_data.get("cost_price", 0)),
                stock=int(product_data.get("stock", 0)),
                min_stock=int(product_data.get("min_stock", 0)),
                max_stock=int(product_data.get("max_stock", 100)),
                category_id=product_data.get("category_id"),
                description=product_data.get("description"),
                is_active=product_data.get("is_active", True)
            )
            
            db.add(product)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Fila {i+1}: {str(e)}")
    
    if imported_count > 0:
        db.commit()
    
    return {
        "imported": imported_count,
        "errors": errors,
        "total_rows": len(products.get("products", []))
    }

# Exportar productos a Excel
@router.get("/export")
def export_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Exportar productos a Excel"""
    products = db.query(Product).filter(Product.is_active == True).all()
    
    # Crear archivo Excel en memoria
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Productos")
    
    # Estilos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#667eea',
        'font_color': 'white',
        'border': 1
    })
    
    # Encabezados
    headers = ['Código', 'Nombre', 'Precio', 'Precio Costo', 'Stock', 'Stock Mínimo', 'Stock Máximo', 'Categoría', 'Descripción', 'Activo']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Datos
    for row, product in enumerate(products, 1):
        worksheet.write(row, 0, product.code)
        worksheet.write(row, 1, product.name)
        worksheet.write(row, 2, product.price)
        worksheet.write(row, 3, product.cost_price or 0)
        worksheet.write(row, 4, product.stock)
        worksheet.write(row, 5, product.min_stock or 0)
        worksheet.write(row, 6, product.max_stock or 100)
        worksheet.write(row, 7, product.category.name if product.category else '')
        worksheet.write(row, 8, product.description or '')
        worksheet.write(row, 9, 'Sí' if product.is_active else 'No')
    
    workbook.close()
    output.seek(0)
    
    return FileResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="productos.xlsx"
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtener producto por ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.put("/{product_id}/debug")
async def debug_update_product(
    product_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Endpoint de debug para actualizar productos"""
    try:
        print("🔍 Datos recibidos para actualizar:", data)
        
        # Buscar el producto
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        print(f"📦 Producto encontrado: {db_product.name} (ID: {db_product.id})")
        
        # Actualizar campos directamente desde el diccionario
        update_fields = [
            'name', 'code', 'description', 'price', 'cost_price', 'stock', 
            'min_stock', 'max_stock', 'stock_quantity', 'min_stock_level', 
            'unit', 'category_id', 'product_type', 'purchase_price', 
            'supplier_id', 'supplier', 'is_active'
        ]
        
        for field in update_fields:
            if field in data and data[field] is not None:
                old_value = getattr(db_product, field, None)
                new_value = data[field]
                setattr(db_product, field, new_value)
                print(f"  ✅ {field}: {old_value} → {new_value}")
        
        db.commit()
        db.refresh(db_product)
        
        print("✅ Producto actualizado exitosamente")
        return {"success": True, "product": db_product, "message": "Producto actualizado exitosamente"}
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error actualizando producto: {error_details}")
        db.rollback()
        return {"error": str(e), "details": error_details}

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualizar producto"""
    try:
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Actualizar campos
        update_data = {}
        if product.name is not None:
            update_data["name"] = product.name
        if product.price is not None:
            update_data["price"] = product.price
        if product.cost_price is not None:
            update_data["cost_price"] = product.cost_price
        if product.stock is not None:
            update_data["stock"] = product.stock
        if product.min_stock is not None:
            update_data["min_stock"] = product.min_stock
        if product.max_stock is not None:
            update_data["max_stock"] = product.max_stock
        if product.stock_quantity is not None:
            update_data["stock_quantity"] = product.stock_quantity
        if product.min_stock_level is not None:
            update_data["min_stock_level"] = product.min_stock_level
        if product.unit is not None:
            update_data["unit"] = product.unit
        if product.category_id is not None:
            update_data["category_id"] = product.category_id
        if product.product_type is not None:
            update_data["product_type"] = product.product_type
        if product.purchase_price is not None:
            update_data["purchase_price"] = product.purchase_price
        if product.supplier_id is not None:
            update_data["supplier_id"] = product.supplier_id
        if product.supplier is not None:
            update_data["supplier"] = product.supplier
        if product.description is not None:
            update_data["description"] = product.description
        if product.is_active is not None:
            update_data["is_active"] = product.is_active
        
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        return db_product
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error actualizando producto: {str(e)}")

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

# Descargar plantilla de importación
@router.get("/export-template")
def export_template(
    current_user: User = Depends(get_current_active_user)
):
    """Descargar plantilla para importar productos"""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Plantilla")
    
    # Estilos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#28a745',
        'font_color': 'white',
        'border': 1
    })
    
    note_format = workbook.add_format({
        'italic': True,
        'font_color': '#6c757d'
    })
    
    # Encabezados
    headers = ['Nombre*', 'Precio*', 'Precio Costo', 'Stock', 'Stock Mínimo', 'Stock Máximo', 'Categoría ID', 'Descripción', 'Activo']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Notas
    worksheet.write(2, 0, "Notas:", note_format)
    worksheet.write(3, 0, "- Los campos marcados con * son obligatorios")
    worksheet.write(4, 0, "- El código se generará automáticamente")
    worksheet.write(5, 0, "- Precio y Precio Costo deben ser números decimales")
    worksheet.write(6, 0, "- Stock, Stock Mínimo y Stock Máximo deben ser números enteros")
    worksheet.write(7, 0, "- Activo debe ser 'Sí' o 'No'")
    
    # Ejemplo
    worksheet.write(9, 0, "Ejemplo:", note_format)
    worksheet.write(10, 0, "Hamburguesa Clásica")
    worksheet.write(10, 1, 12.50)
    worksheet.write(10, 2, 8.00)
    worksheet.write(10, 3, 50)
    worksheet.write(10, 4, 10)
    worksheet.write(10, 5, 100)
    worksheet.write(10, 6, 1)
    worksheet.write(10, 7, "Hamburguesa con carne, lechuga, tomate y queso")
    worksheet.write(10, 8, "Sí")
    
    workbook.close()
    output.seek(0)
    
    return FileResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="plantilla_productos.xlsx"
    )




@router.get("/inventory/low-stock")
def get_inventory_low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener productos de inventario con stock bajo"""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.INVENTORY,
        Product.stock_quantity <= Product.min_stock_level
    ).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "stock_quantity": p.stock_quantity,
            "min_stock_level": p.min_stock_level,
            "purchase_price": float(p.purchase_price or 0),
            "unit": p.unit,
            "supplier_name": p.supplier.name if p.supplier else None,
            "needs_reorder": p.stock_quantity <= p.reorder_point
        }
        for p in products
    ]


@router.get("/inventory/statistics")
def get_inventory_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estadísticas de productos de inventario"""
    # Total de productos de inventario
    total_inventory = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.INVENTORY
    ).count()
    
    # Productos con stock bajo
    low_stock_inventory = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.INVENTORY,
        Product.stock_quantity <= Product.min_stock_level
    ).count()
    
    # Productos agotados
    out_of_stock_inventory = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.INVENTORY,
        Product.stock_quantity == 0
    ).count()
    
    # Valor total del inventario
    total_value = db.query(func.sum(Product.stock_quantity * Product.purchase_price))\
        .filter(
            Product.is_active == True,
            Product.product_type == ProductType.INVENTORY
        ).scalar() or 0
    
    return {
        "total_inventory_products": total_inventory,
        "low_stock_products": low_stock_inventory,
        "out_of_stock_products": out_of_stock_inventory,
        "total_inventory_value": float(total_value)
    }


@router.get("/sales/statistics")
def get_sales_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estadísticas de productos de venta"""
    # Total de productos de venta
    total_sales = db.query(Product).filter(
        Product.is_active == True,
        Product.product_type == ProductType.SALES
    ).count()
    
    # Productos con recetas
    from app.models.recipe import Recipe
    products_with_recipes = db.query(Product).join(Recipe).filter(
        Product.is_active == True,
        Product.product_type == ProductType.SALES,
        Recipe.is_active == True
    ).count()
    
    # Productos sin recetas
    products_without_recipes = total_sales - products_with_recipes
    
    return {
        "total_sales_products": total_sales,
        "products_with_recipes": products_with_recipes,
        "products_without_recipes": products_without_recipes
    }


# Esquemas para ajuste de stock
class StockAdjustmentRequest(BaseModel):
    product_id: int
    adjustment_type: str  # 'entrada', 'salida', 'ajuste'
    quantity: float
    reason: Optional[str] = None

class StockAdjustmentResponse(BaseModel):
    product_id: int
    product_name: str
    previous_stock: float
    new_stock: float
    adjustment_type: str
    quantity: float
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/inventory/adjust", response_model=StockAdjustmentResponse)
def adjust_inventory_stock(
    request: StockAdjustmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ajustar el stock de un producto de inventario"""
    try:
        # Obtener el producto
        product = db.query(Product).filter(
            Product.id == request.product_id,
            Product.product_type == ProductType.INVENTORY,
            Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        # Calcular nuevo stock
        previous_stock = product.stock_quantity or 0
        
        if request.adjustment_type == "entrada":
            new_stock = previous_stock + request.quantity
        elif request.adjustment_type == "salida":
            new_stock = previous_stock - request.quantity
        elif request.adjustment_type == "ajuste":
            new_stock = request.quantity
        else:
            raise HTTPException(status_code=400, detail="Tipo de ajuste inválido")
        
        # Validar que el stock no sea negativo
        if new_stock < 0:
            raise HTTPException(status_code=400, detail="El stock no puede ser negativo")
        
        # Actualizar el producto
        product.stock_quantity = new_stock
        product.stock = new_stock  # Sincronizar campo alias
        
        # Crear movimiento de inventario
        
        movement = InventoryMovement(
            product_id=product.id,
            user_id=current_user.id,
            adjustment_type=request.adjustment_type,
            reason=request.reason or f"Ajuste de stock - {request.adjustment_type}",
            quantity=abs(request.quantity),
            previous_stock=previous_stock,
            new_stock=new_stock,
            notes=request.reason
        )
        
        db.add(movement)
        db.commit()
        db.refresh(product)
        
        return StockAdjustmentResponse(
            product_id=product.id,
            product_name=product.name,
            previous_stock=previous_stock,
            new_stock=new_stock,
            adjustment_type=request.adjustment_type,
            quantity=request.quantity,
            reason=request.reason,
            created_at=movement.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error ajustando stock: {str(e)}")


# Esquemas para histórico de movimientos
class InventoryMovementResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_code: str
    movement_type: str
    reason: str
    quantity: float
    previous_stock: float
    new_stock: float
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    user_name: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/inventory/movements/debug")
def debug_inventory_movements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Debug endpoint para movimientos de inventario"""
    try:
        # Consulta simple sin JOINs
        movements = db.query(InventoryMovement).limit(5).all()
        
        result = []
        for movement in movements:
            result.append({
                "id": movement.id,
                "product_id": movement.product_id,
                "user_id": movement.user_id,
                "adjustment_type": movement.adjustment_type,
                "quantity": movement.quantity,
                "previous_stock": movement.previous_stock,
                "new_stock": movement.new_stock,
                "reason": movement.reason,
                "notes": movement.notes,
                "created_at": movement.created_at.isoformat() if movement.created_at else None
            })
        
        return {
            "success": True,
            "count": len(result),
            "movements": result
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error en debug: {error_details}")
        return {
            "error": str(e),
            "details": error_details
        }

@router.get("/inventory/movements", response_model=List[InventoryMovementResponse])
def get_inventory_movements(
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    product_id: Optional[int] = Query(None, description="ID del producto"),
    movement_type: Optional[str] = Query(None, description="Tipo de movimiento"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener histórico de movimientos de inventario"""
    try:
        
        # Construir consulta base (sin JOIN con User por ahora)
        query = db.query(InventoryMovement).join(Product)
        
        # Aplicar filtros
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(InventoryMovement.created_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(InventoryMovement.created_at < end_datetime)
        
        if product_id:
            query = query.filter(InventoryMovement.product_id == product_id)
        
        if movement_type:
            query = query.filter(InventoryMovement.adjustment_type == movement_type)
        
        # Ordenar por fecha más reciente primero
        query = query.order_by(InventoryMovement.created_at.desc())
        
        # Aplicar paginación
        movements = query.offset(skip).limit(limit).all()
        
        # Convertir a respuesta
        result = []
        for movement in movements:
            result.append(InventoryMovementResponse(
                id=movement.id,
                product_id=movement.product_id,
                product_name=movement.product.name,
                product_code=movement.product.code,
                movement_type=movement.adjustment_type,
                reason=movement.reason,
                quantity=float(movement.quantity),
                previous_stock=float(movement.previous_stock),
                new_stock=float(movement.new_stock),
                unit_cost=None,  # No disponible en la estructura actual
                total_cost=None,  # No disponible en la estructura actual
                reference_type=None,  # No disponible en la estructura actual
                reference_id=None,  # No disponible en la estructura actual
                reference_number=None,  # No disponible en la estructura actual
                notes=movement.notes,
                user_name=f"Usuario {movement.user_id}",
                created_at=movement.created_at
            ))
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error obteniendo movimientos: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo movimientos: {str(e)}")


@router.get("/inventory/movements/summary")
def get_inventory_movements_summary(
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener resumen de movimientos de inventario por día"""
    try:
        from sqlalchemy import func, cast, Date
        
        # Construir consulta base
        query = db.query(
            cast(InventoryMovement.created_at, Date).label('date'),
            InventoryMovement.adjustment_type,
            func.count(InventoryMovement.id).label('count'),
            func.sum(InventoryMovement.quantity).label('total_quantity')
        ).join(Product).filter(
            Product.product_type == ProductType.INVENTORY
        )
        
        # Aplicar filtros de fecha
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(InventoryMovement.created_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(InventoryMovement.created_at < end_datetime)
        
        # Agrupar por fecha y tipo de movimiento
        query = query.group_by(
            cast(InventoryMovement.created_at, Date),
            InventoryMovement.adjustment_type
        ).order_by(
            cast(InventoryMovement.created_at, Date).desc(),
            InventoryMovement.adjustment_type
        )
        
        results = query.all()
        
        # Organizar datos por fecha
        summary = {}
        for result in results:
            date_str = result.date.strftime("%Y-%m-%d")
            if date_str not in summary:
                summary[date_str] = {
                    "date": date_str,
                    "movements": {},
                    "total_movements": 0,
                    "total_quantity": 0,
                    "total_cost": 0
                }
            
            movement_type = result.adjustment_type
            summary[date_str]["movements"][movement_type] = {
                "count": result.count,
                "quantity": float(result.total_quantity or 0),
                "cost": 0  # No disponible en la estructura actual
            }
            summary[date_str]["total_movements"] += result.count
            summary[date_str]["total_quantity"] += float(result.total_quantity or 0)
            summary[date_str]["total_cost"] += 0  # No disponible en la estructura actual
        
        return {
            "success": True,
            "summary": list(summary.values()),
            "total_days": len(summary)
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error obteniendo resumen: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen: {str(e)}") 