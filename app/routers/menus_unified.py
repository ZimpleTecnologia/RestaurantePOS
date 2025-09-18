"""
Router unificado para el sistema de Gestión de Menús
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.user import User, UserRole
from app.models.menu_unified import Menu, Plato
from app.schemas.menu_unified import (
    MenuCreate, MenuUpdate, MenuResponse, MenuDelDiaResponse,
    PlatoCreate, PlatoUpdate, PlatoResponse, PlatoListResponse,
    MenuListResponse
)
from app.auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/menus", tags=["menús"])


# ============================================================================
# ENDPOINTS PARA PLATOS
# ============================================================================

@router.get("/platos/", response_model=PlatoListResponse)
def get_platos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tipo: Optional[str] = Query(None, pattern=r'^(Fijo|Variable)$'),
    categoria: Optional[str] = None,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener lista de platos"""
    query = db.query(Plato)
    
    if tipo:
        query = query.filter(Plato.tipo == tipo)
    if categoria:
        query = query.filter(Plato.categoria == categoria)
    if activo is not None:
        query = query.filter(Plato.activo == activo)
    
    total = query.count()
    platos = query.offset(skip).limit(limit).all()
    
    return PlatoListResponse(
        platos=platos,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.post("/platos/", response_model=PlatoResponse, status_code=status.HTTP_201_CREATED)
def create_plato(
    plato: PlatoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crear un nuevo plato (ADMIN)"""
    db_plato = Plato(**plato.dict())
    db.add(db_plato)
    db.commit()
    db.refresh(db_plato)
    return db_plato


@router.get("/platos/{plato_id}", response_model=PlatoResponse)
def get_plato(
    plato_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener un plato específico"""
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    return plato


@router.put("/platos/{plato_id}", response_model=PlatoResponse)
def update_plato(
    plato_id: int,
    plato_update: PlatoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualizar un plato (ADMIN)"""
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    update_data = plato_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plato, field, value)
    
    db.commit()
    db.refresh(plato)
    return plato


@router.delete("/platos/{plato_id}")
def delete_plato(
    plato_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Eliminar un plato (ADMIN)"""
    plato = db.query(Plato).filter(Plato.id == plato_id).first()
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    db.delete(plato)
    db.commit()
    return {"message": "Plato eliminado exitosamente"}


# ============================================================================
# ENDPOINTS PARA MENÚS
# ============================================================================

@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
def create_menu(
    menu: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crear un nuevo menú (ADMIN)"""
    # Verificar que no exista un menú para esa fecha
    existing_menu = db.query(Menu).filter(Menu.fecha == menu.fecha).first()
    if existing_menu:
        raise HTTPException(
            status_code=400, 
            detail="Ya existe un menú para esta fecha"
        )
    
    # Verificar que todos los platos existan
    platos = db.query(Plato).filter(Plato.id.in_(menu.platos_ids)).all()
    if len(platos) != len(menu.platos_ids):
        raise HTTPException(
            status_code=400,
            detail="Algunos platos no existen"
        )
    
    # Crear el menú
    menu_data = menu.dict(exclude={'platos_ids'})
    db_menu = Menu(**menu_data)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    
    # Asociar platos al menú
    db_menu.platos = platos
    db.commit()
    db.refresh(db_menu)
    
    return db_menu


@router.get("/{fecha}", response_model=MenuDelDiaResponse)
def get_menu_by_date(
    fecha: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener menú de una fecha específica"""
    menu = db.query(Menu).filter(Menu.fecha == fecha).first()
    if not menu:
        raise HTTPException(
            status_code=404,
            detail=f"No hay menú disponible para la fecha {fecha}"
        )
    
    # Organizar platos por tipo
    platos_fijos = [plato for plato in menu.platos if plato.tipo == 'Fijo']
    platos_variables = [plato for plato in menu.platos if plato.tipo == 'Variable']
    
    # Organizar platos variables por categoría
    platos_por_categoria = {}
    for plato in platos_variables:
        categoria = plato.categoria or 'Otro'
        if categoria not in platos_por_categoria:
            platos_por_categoria[categoria] = []
        platos_por_categoria[categoria].append(plato)
    
    return MenuDelDiaResponse(
        menu=menu,
        platos_fijos=platos_fijos,
        platos_variables=platos_variables,
        platos_por_categoria=platos_por_categoria
    )


@router.get("/", response_model=MenuListResponse)
def get_menus(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener lista de menús"""
    query = db.query(Menu)
    
    if activo is not None:
        query = query.filter(Menu.activo == activo)
    
    total = query.count()
    menus = query.order_by(Menu.fecha.desc()).offset(skip).limit(limit).all()
    
    return MenuListResponse(
        menus=menus,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.put("/{menu_id}", response_model=MenuResponse)
def update_menu(
    menu_id: int,
    menu_update: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualizar un menú (ADMIN)"""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    
    # Actualizar campos del menú
    update_data = menu_update.dict(exclude_unset=True, exclude={'platos_ids'})
    for field, value in update_data.items():
        setattr(menu, field, value)
    
    # Actualizar platos si se proporcionan
    if menu_update.platos_ids is not None:
        # Verificar que todos los platos existan
        platos = db.query(Plato).filter(Plato.id.in_(menu_update.platos_ids)).all()
        if len(platos) != len(menu_update.platos_ids):
            raise HTTPException(
                status_code=400,
                detail="Algunos platos no existen"
            )
        menu.platos = platos
    
    db.commit()
    db.refresh(menu)
    return menu


@router.delete("/{menu_id}")
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Desactivar un menú (ADMIN)"""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    
    menu.activo = False
    db.commit()
    
    return {"message": "Menú desactivado exitosamente"}


# ============================================================================
# ENDPOINTS ESPECIALES
# ============================================================================

@router.get("/hoy/menu", response_model=MenuDelDiaResponse)
def get_today_menu(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener menú del día actual"""
    today = date.today()
    return get_menu_by_date(today, db, current_user)


@router.get("/platos/fijos/", response_model=List[PlatoResponse])
def get_platos_fijos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener solo platos fijos"""
    platos = db.query(Plato).filter(
        Plato.tipo == 'Fijo',
        Plato.activo == True
    ).all()
    return platos


@router.get("/platos/variables/", response_model=List[PlatoResponse])
def get_platos_variables(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener solo platos variables"""
    platos = db.query(Plato).filter(
        Plato.tipo == 'Variable',
        Plato.activo == True
    ).all()
    return platos
