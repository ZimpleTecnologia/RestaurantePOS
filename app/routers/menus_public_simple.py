"""
Router público simple para probar el sistema de menús sin autenticación
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

router = APIRouter(prefix="/public/menus", tags=["menús públicos"])


@router.get("/platos/")
def get_platos_public(db: Session = Depends(get_db)):
    """Obtener lista de platos (público)"""
    try:
        result = db.execute(text("SELECT * FROM platos WHERE activo = TRUE ORDER BY nombre"))
        platos = []
        for row in result:
            platos.append({
                "id": row[0],
                "nombre": row[1],
                "descripcion": row[2],
                "precio": row[3],
                "tipo": row[4],
                "categoria": row[5],
                "activo": row[6],
                "created_at": str(row[7]) if row[7] else None,
                "updated_at": str(row[8]) if row[8] else None
            })
        return platos
    except Exception as e:
        return {"error": str(e)}


@router.get("/")
def get_menus_public(db: Session = Depends(get_db)):
    """Obtener lista de menús (público)"""
    try:
        result = db.execute(text("SELECT * FROM menus WHERE activo = TRUE ORDER BY fecha DESC"))
        menus = []
        for row in result:
            menus.append({
                "id": row[0],
                "fecha": str(row[1]),
                "activo": row[2],
                "nombre": row[3],
                "descripcion": row[4],
                "created_at": str(row[5]) if row[5] else None,
                "updated_at": str(row[6]) if row[6] else None
            })
        return menus
    except Exception as e:
        return {"error": str(e)}


@router.get("/hoy/")
def get_menu_hoy_public(db: Session = Depends(get_db)):
    """Obtener menú de hoy (público)"""
    try:
        from datetime import date
        today = date.today()
        
        result = db.execute(text("""
            SELECT * FROM menus 
            WHERE fecha = :fecha AND activo = TRUE
        """), {"fecha": today})
        
        row = result.fetchone()
        if not row:
            return {"message": "No hay menú para hoy"}
        
        menu = {
            "id": row[0],
            "fecha": str(row[1]),
            "activo": row[2],
            "nombre": row[3],
            "descripcion": row[4],
            "created_at": str(row[5]) if row[5] else None,
            "updated_at": str(row[6]) if row[6] else None
        }
        
        return menu
    except Exception as e:
        return {"error": str(e)}


@router.get("/stats/")
def get_menu_stats_public(db: Session = Depends(get_db)):
    """Obtener estadísticas del sistema (público)"""
    try:
        from datetime import date
        
        # Contar platos
        result = db.execute(text("SELECT COUNT(*) FROM platos"))
        total_platos = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM platos WHERE activo = TRUE"))
        platos_activos = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM platos WHERE tipo = 'Fijo' AND activo = TRUE"))
        platos_fijos = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM platos WHERE tipo = 'Variable' AND activo = TRUE"))
        platos_variables = result.fetchone()[0]
        
        # Contar menús
        result = db.execute(text("SELECT COUNT(*) FROM menus"))
        total_menus = result.fetchone()[0]
        
        result = db.execute(text("SELECT COUNT(*) FROM menus WHERE activo = TRUE"))
        menus_activos = result.fetchone()[0]
        
        # Verificar si hay menú para hoy
        today = date.today()
        result = db.execute(text("SELECT COUNT(*) FROM menus WHERE fecha = :fecha AND activo = TRUE"), {"fecha": today})
        tiene_menu_hoy = result.fetchone()[0] > 0
        
        return {
            "platos": {
                "total": total_platos,
                "activos": platos_activos,
                "fijos": platos_fijos,
                "variables": platos_variables
            },
            "menus": {
                "total": total_menus,
                "activos": menus_activos,
                "tiene_menu_hoy": tiene_menu_hoy
            },
            "sistema": {
                "estado": "funcionando",
                "version": "1.0.0"
            }
        }
    except Exception as e:
        return {"error": str(e)}
