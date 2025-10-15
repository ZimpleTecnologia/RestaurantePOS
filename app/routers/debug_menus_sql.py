from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/debug-sql", tags=["debug-sql"])

@router.get("/menus-raw")
def get_menus_raw_sql(db: Session = Depends(get_db)):
    """Endpoint de debug usando SQL directo"""
    try:
        # Consulta SQL directa
        result = db.execute(text("""
            SELECT menu_id, fecha, nombre, precio, estado, descripcion, created_at, updated_at
            FROM menus_dia
            ORDER BY fecha DESC
        """)).fetchall()
        
        menus = []
        for row in result:
            menus.append({
                "menu_id": row.menu_id,
                "fecha": str(row.fecha),
                "nombre": row.nombre,
                "precio": float(row.precio),
                "estado": row.estado,
                "descripcion": row.descripcion,
                "created_at": str(row.created_at) if row.created_at else None,
                "updated_at": str(row.updated_at) if row.updated_at else None
            })
        
        return {"menus": menus, "total": len(menus)}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/menus-count")
def get_menus_count_sql(db: Session = Depends(get_db)):
    """Endpoint de debug para contar menús usando SQL directo"""
    try:
        result = db.execute(text("SELECT COUNT(*) FROM menus_dia")).scalar()
        return {"count": result}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/menus-first")
def get_first_menu_sql(db: Session = Depends(get_db)):
    """Endpoint de debug para obtener el primer menú usando SQL directo"""
    try:
        result = db.execute(text("""
            SELECT menu_id, fecha, nombre, precio, estado, descripcion
            FROM menus_dia
            ORDER BY fecha DESC
            LIMIT 1
        """)).fetchone()
        
        if result:
            return {
                "menu_id": result.menu_id,
                "fecha": str(result.fecha),
                "nombre": result.nombre,
                "precio": float(result.precio),
                "estado": result.estado,
                "descripcion": result.descripcion
            }
        else:
            return {"message": "No hay menús en la base de datos"}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


