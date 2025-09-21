from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.restaurant_menu import MenuDia

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/menus-raw")
def get_menus_raw(db: Session = Depends(get_db)):
    """Endpoint de debug para obtener menús sin schema"""
    try:
        # Consulta simple sin filtros
        menus = db.query(MenuDia).all()
        
        result = []
        for menu in menus:
            result.append({
                "id": menu.id,
                "fecha": str(menu.fecha),
                "nombre": menu.nombre,
                "precio": float(menu.precio),
                "estado": menu.estado
            })
        
        return {"menus": result, "total": len(result)}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/menus-count")
def get_menus_count(db: Session = Depends(get_db)):
    """Endpoint de debug para contar menús"""
    try:
        count = db.query(MenuDia).count()
        return {"count": count}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/menus-first")
def get_first_menu(db: Session = Depends(get_db)):
    """Endpoint de debug para obtener el primer menú"""
    try:
        menu = db.query(MenuDia).first()
        if menu:
            return {
                "id": menu.id,
                "fecha": str(menu.fecha),
                "nombre": menu.nombre,
                "precio": float(menu.precio),
                "estado": menu.estado
            }
        else:
            return {"message": "No hay menús en la base de datos"}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/menus-sql")
def get_menus_sql(db: Session = Depends(get_db)):
    """Endpoint de debug usando SQL directo"""
    try:
        from sqlalchemy import text
        # Consulta SQL directa
        result = db.execute(text("""
            SELECT menu_id, fecha, nombre, precio, estado, descripcion
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
                "descripcion": row.descripcion
            })
        
        return {"menus": menus, "total": len(menus)}
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/menu-hoy-debug")
def get_menu_hoy_debug(db: Session = Depends(get_db)):
    """Endpoint de debug para menú de hoy"""
    try:
        from datetime import date
        today = date.today()
        
        # Buscar menú del día
        menu = db.query(MenuDia).filter(
            MenuDia.fecha == today,
            MenuDia.estado == 'ACTIVE'
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
                "fecha": str(menu.fecha),
                "nombre": menu.nombre,
                "precio": float(menu.precio),
                "estado": menu.estado
            },
            "mensaje": "Menú encontrado"
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/menu-hoy-detailed")
def get_menu_hoy_detailed(db: Session = Depends(get_db)):
    """Endpoint de debug detallado para menú de hoy"""
    try:
        from datetime import date
        today = date.today()
        
        # Paso 1: Buscar menú del día
        menu = db.query(MenuDia).filter(
            MenuDia.fecha == today,
            MenuDia.estado == 'ACTIVE'
        ).first()
        
        if not menu:
            return {
                "menu": None,
                "mensaje": "No hay menú publicado para hoy",
                "fecha_buscada": str(today)
            }
        
        # Paso 2: Obtener acompañamientos fijos
        try:
            acompanamientos = db.query(AcompanamientoFijo).filter(AcompanamientoFijo.activo == True).order_by(AcompanamientoFijo.orden).all()
            acompanamientos_data = []
            for a in acompanamientos:
                acompanamientos_data.append({
                    "id": a.id,
                    "nombre": a.nombre,
                    "descripcion": a.descripcion,
                    "activo": a.activo,
                    "orden": a.orden
                })
        except Exception as e:
            acompanamientos_data = []
        
        # Paso 3: Obtener platos fijos
        try:
            platos_fijos = db.query(PlatoRestaurante).filter(
                PlatoRestaurante.tipo == 'Plato_Fijo',
                PlatoRestaurante.activo == True
            ).order_by(PlatoRestaurante.nombre).all()
            platos_fijos_data = []
            for p in platos_fijos:
                platos_fijos_data.append({
                    "id": p.id,
                    "nombre": p.nombre,
                    "descripcion": p.descripcion,
                    "precio": float(p.precio),
                    "tipo": p.tipo
                })
        except Exception as e:
            platos_fijos_data = []
        
        return {
            "menu": {
                "id": menu.id,
                "fecha": str(menu.fecha),
                "nombre": menu.nombre,
                "precio": float(menu.precio),
                "estado": menu.estado
            },
            "categorias": {},  # Vacío por ahora
            "acompanamientos_fijos": acompanamientos_data,
            "platos_fijos": platos_fijos_data,
            "mensaje": "Menú encontrado"
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}
