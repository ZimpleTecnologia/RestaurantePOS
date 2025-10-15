"""
Router de prueba simple para identificar el problema
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.restaurant_menu import CategoriaMenuRestaurante

router = APIRouter(prefix="/test", tags=["test"])

@router.get("/categorias-simple")
def get_categorias_simple(db: Session = Depends(get_db)):
    """Endpoint simple para probar categorías sin schemas complejos"""
    try:
        # Consulta simple
        categorias = db.query(CategoriaMenuRestaurante).limit(5).all()
        
        # Convertir a diccionario simple
        result = []
        for categoria in categorias:
            result.append({
                "id": categoria.id,
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion,
                "orden": categoria.orden,
                "is_active": categoria.is_active
            })
        
        return {"categorias": result, "total": len(result)}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/categorias-raw")
def get_categorias_raw(db: Session = Depends(get_db)):
    """Endpoint para probar consulta raw"""
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT id, nombre, descripcion, orden, is_active FROM categorias_menu LIMIT 5"))
        rows = result.fetchall()
        
        categorias = []
        for row in rows:
            categorias.append({
                "id": row[0],
                "nombre": row[1], 
                "descripcion": row[2],
                "orden": row[3],
                "is_active": row[4]
            })
        
        return {"categorias": categorias, "total": len(categorias)}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/categorias-schema-test")
def get_categorias_schema_test(db: Session = Depends(get_db)):
    """Endpoint para probar schema simple"""
    try:
        from app.schemas.restaurant_menu import CategoriaMenuResponse
        from app.models.restaurant_menu import CategoriaMenuRestaurante
        
        # Obtener una categoría
        categoria = db.query(CategoriaMenuRestaurante).first()
        if not categoria:
            return {"error": "No hay categorías en la base de datos"}
        
        # Intentar serializar
        try:
            categoria_dict = {
                "id": categoria.id,
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion,
                "orden": categoria.orden,
                "is_active": categoria.is_active,
                "created_at": str(categoria.created_at) if categoria.created_at else None,
                "updated_at": str(categoria.updated_at) if categoria.updated_at else None
            }
            return {"categoria": categoria_dict, "success": True}
        except Exception as serialize_error:
            return {"error": f"Error serializando: {str(serialize_error)}", "type": type(serialize_error).__name__}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/categorias-exact-copy")
def get_categorias_exact_copy(
    skip: int = 0,
    limit: int = 100,
    activo: bool = None,
    db: Session = Depends(get_db)
):
    """Endpoint que copia exactamente la lógica del endpoint original"""
    try:
        from app.schemas.restaurant_menu import CategoriaMenuListResponse
        from app.models.restaurant_menu import CategoriaMenuRestaurante
        
        query = db.query(CategoriaMenuRestaurante)
        
        if activo is not None:
            query = query.filter(CategoriaMenuRestaurante.is_active == activo)
        
        total = query.count()
        categorias = query.order_by(CategoriaMenuRestaurante.orden, CategoriaMenuRestaurante.nombre).offset(skip).limit(limit).all()
        
        return CategoriaMenuListResponse(categorias=categorias, total=total)
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/menu-hoy-simple")
def get_menu_hoy_simple(db: Session = Depends(get_db)):
    """Endpoint simple para probar menú de hoy"""
    try:
        from app.models.restaurant_menu import MenuDia
        from datetime import date
        
        today = date.today()
        
        # Buscar menú del día
        menu = db.query(MenuDia).filter(
            MenuDia.fecha == today,
            MenuDia.activo == True,
            MenuDia.publicado == True
        ).first()
        
        if not menu:
            return {
                "menu": None,
                "mensaje": "No hay menú publicado para hoy",
                "fecha_buscada": str(today)
            }
        
        return {
            "menu": {
                "id": menu.id,
                "nombre": menu.nombre,
                "fecha": str(menu.fecha),
                "precio": float(menu.precio),
                "descripcion": menu.descripcion
            },
            "mensaje": "Menú encontrado"
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}
