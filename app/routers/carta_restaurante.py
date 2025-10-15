"""
Router para el sistema de Carta Restaurante
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models.carta_restaurante import CartaRestaurante, MenuDia, MenuOpcion, TipoPlato
from app.models.user import User
from app.schemas.carta_restaurante import (
    CartaRestauranteCreate, CartaRestauranteUpdate, CartaRestauranteResponse,
    MenuDiaCreate, MenuDiaUpdate, MenuDiaResponse,
    MenuOpcionCreate, MenuOpcionResponse,
    CartaStatsResponse, MenuStatsResponse, MenuHoyResponse
)
from app.auth import get_current_active_user, require_admin

router = APIRouter(prefix="/carta", tags=["carta-restaurante"])

# ==================== ENDPOINTS PARA CARTA RESTAURANTE ====================

@router.get("/", response_model=List[CartaRestauranteResponse])
def get_carta(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: 'Fijo' o 'Variable'"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de platos de la carta"""
    query = db.query(CartaRestaurante)
    
    # Aplicar filtros
    if tipo:
        query = query.filter(CartaRestaurante.tipo == tipo)
    
    if categoria:
        query = query.filter(CartaRestaurante.categoria == categoria)
    
    if activo is not None:
        query = query.filter(CartaRestaurante.activo == activo)
    
    if search:
        query = query.filter(CartaRestaurante.nombre.ilike(f"%{search}%"))
    
    platos = query.offset(skip).limit(limit).all()
    return platos


@router.get("/fijos", response_model=List[CartaRestauranteResponse])
def get_platos_fijos(
    activo: bool = Query(True, description="Solo platos activos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener platos fijos de la carta"""
    query = db.query(CartaRestaurante).filter(CartaRestaurante.tipo == TipoPlato.FIJO)
    
    if activo:
        query = query.filter(CartaRestaurante.activo == True)
    
    platos = query.all()
    return platos


@router.get("/variables", response_model=List[CartaRestauranteResponse])
def get_platos_variables(
    activo: bool = Query(True, description="Solo platos activos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener platos variables de la carta"""
    query = db.query(CartaRestaurante).filter(CartaRestaurante.tipo == TipoPlato.VARIABLE)
    
    if activo:
        query = query.filter(CartaRestaurante.activo == True)
    
    platos = query.all()
    return platos


@router.get("/{plato_id}", response_model=CartaRestauranteResponse)
def get_plato(
    plato_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un plato por ID"""
    plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == plato_id).first()
    if not plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    return plato


@router.post("/", response_model=CartaRestauranteResponse, status_code=status.HTTP_201_CREATED)
def create_plato(
    plato: CartaRestauranteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crear un nuevo plato"""
    db_plato = CartaRestaurante(**plato.dict())
    db.add(db_plato)
    db.commit()
    db.refresh(db_plato)
    return db_plato


@router.put("/{plato_id}", response_model=CartaRestauranteResponse)
def update_plato(
    plato_id: int,
    plato_update: CartaRestauranteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualizar un plato"""
    db_plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == plato_id).first()
    if not db_plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    update_data = plato_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_plato, field, value)
    
    db.commit()
    db.refresh(db_plato)
    return db_plato


@router.delete("/{plato_id}")
def delete_plato(
    plato_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Eliminar un plato"""
    db_plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == plato_id).first()
    if not db_plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    # Verificar si está en algún menú
    menu_count = db.query(MenuOpcion).filter(MenuOpcion.producto_id == plato_id).count()
    if menu_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar el plato porque está en {menu_count} menú(s)"
        )
    
    db.delete(db_plato)
    db.commit()
    return {"message": "Plato eliminado exitosamente"}


# ==================== ENDPOINTS PARA MENÚ DEL DÍA ====================

@router.get("/menus/", response_model=List[MenuDiaResponse])
def get_menus(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener lista de menús del día"""
    query = db.query(MenuDia)
    
    if activo is not None:
        query = query.filter(MenuDia.activo == activo)
    
    menus = query.order_by(MenuDia.fecha.desc()).offset(skip).limit(limit).all()
    return menus


@router.get("/menus/hoy", response_model=MenuHoyResponse)
def get_menu_hoy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener menú del día actual"""
    hoy = date.today().strftime('%Y-%m-%d')
    
    menu = db.query(MenuDia).filter(
        MenuDia.fecha == hoy,
        MenuDia.activo == True
    ).first()
    
    if not menu:
        return MenuHoyResponse(menu=None, platos_fijos=[], platos_variables_por_categoria={})
    
    # Obtener platos fijos
    platos_fijos = [opcion.producto for opcion in menu.get_platos_fijos()]
    
    # Obtener platos variables por categoría
    platos_variables = menu.get_platos_variables()
    platos_variables_por_categoria = {}
    
    for opcion in platos_variables:
        categoria = opcion.producto.categoria or "Otro"
        if categoria not in platos_variables_por_categoria:
            platos_variables_por_categoria[categoria] = []
        platos_variables_por_categoria[categoria].append(opcion.producto)
    
    return MenuHoyResponse(
        menu=menu,
        platos_fijos=platos_fijos,
        platos_variables_por_categoria=platos_variables_por_categoria
    )


@router.get("/menus/{menu_id}", response_model=MenuDiaResponse)
def get_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener un menú por ID"""
    menu = db.query(MenuDia).filter(MenuDia.menu_id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    return menu


@router.post("/menus/", response_model=MenuDiaResponse, status_code=status.HTTP_201_CREATED)
def create_menu(
    menu: MenuDiaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crear un nuevo menú del día"""
    # Verificar que no exista un menú para esa fecha
    existing_menu = db.query(MenuDia).filter(MenuDia.fecha == menu.fecha).first()
    if existing_menu:
        raise HTTPException(status_code=400, detail="Ya existe un menú para esta fecha")
    
    # Crear el menú
    menu_data = menu.dict(exclude={'platos_fijos', 'platos_variables'})
    db_menu = MenuDia(**menu_data)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    
    # Agregar platos fijos
    for plato_id in menu.platos_fijos:
        plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == plato_id).first()
        if plato and plato.tipo == TipoPlato.FIJO:
            opcion = MenuOpcion(
                menu_id=db_menu.menu_id,
                producto_id=plato_id,
                es_fijo=True
            )
            db.add(opcion)
    
    # Agregar platos variables
    for plato_id in menu.platos_variables:
        plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == plato_id).first()
        if plato and plato.tipo == TipoPlato.VARIABLE:
            opcion = MenuOpcion(
                menu_id=db_menu.menu_id,
                producto_id=plato_id,
                es_fijo=False
            )
            db.add(opcion)
    
    db.commit()
    db.refresh(db_menu)
    return db_menu


@router.put("/menus/{menu_id}", response_model=MenuDiaResponse)
def update_menu(
    menu_id: int,
    menu_update: MenuDiaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualizar un menú del día"""
    db_menu = db.query(MenuDia).filter(MenuDia.menu_id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    
    # Actualizar datos básicos
    update_data = menu_update.dict(exclude_unset=True, exclude={'platos_fijos', 'platos_variables'})
    for field, value in update_data.items():
        setattr(db_menu, field, value)
    
    # Actualizar platos si se proporcionan
    if menu_update.platos_fijos is not None or menu_update.platos_variables is not None:
        # Eliminar opciones existentes
        db.query(MenuOpcion).filter(MenuOpcion.menu_id == menu_id).delete()
        
        # Agregar platos fijos
        if menu_update.platos_fijos:
            for plato_id in menu_update.platos_fijos:
                plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == plato_id).first()
                if plato and plato.tipo == TipoPlato.FIJO:
                    opcion = MenuOpcion(
                        menu_id=menu_id,
                        producto_id=plato_id,
                        es_fijo=True
                    )
                    db.add(opcion)
        
        # Agregar platos variables
        if menu_update.platos_variables:
            for plato_id in menu_update.platos_variables:
                plato = db.query(CartaRestaurante).filter(CartaRestaurante.producto_id == plato_id).first()
                if plato and plato.tipo == TipoPlato.VARIABLE:
                    opcion = MenuOpcion(
                        menu_id=menu_id,
                        producto_id=plato_id,
                        es_fijo=False
                    )
                    db.add(opcion)
    
    db.commit()
    db.refresh(db_menu)
    return db_menu


@router.delete("/menus/{menu_id}")
def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Eliminar un menú del día"""
    db_menu = db.query(MenuDia).filter(MenuDia.menu_id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    
    # Verificar si hay pedidos asociados
    from app.models.order import OrderItem
    orders_count = db.query(OrderItem).filter(OrderItem.menu_id == menu_id).count()
    if orders_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar el menú porque tiene {orders_count} pedido(s) asociado(s)"
        )
    
    db.delete(db_menu)
    db.commit()
    return {"message": "Menú eliminado exitosamente"}


# ==================== ENDPOINTS PARA ESTADÍSTICAS ====================

@router.get("/stats/carta", response_model=CartaStatsResponse)
def get_carta_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estadísticas de la carta"""
    total_platos = db.query(CartaRestaurante).count()
    platos_fijos = db.query(CartaRestaurante).filter(CartaRestaurante.tipo == TipoPlato.FIJO).count()
    platos_variables = db.query(CartaRestaurante).filter(CartaRestaurante.tipo == TipoPlato.VARIABLE).count()
    platos_activos = db.query(CartaRestaurante).filter(CartaRestaurante.activo == True).count()
    platos_inactivos = db.query(CartaRestaurante).filter(CartaRestaurante.activo == False).count()
    
    # Platos por categoría
    platos_por_categoria = {}
    categorias = db.query(CartaRestaurante.categoria).distinct().all()
    for categoria in categorias:
        if categoria[0]:
            count = db.query(CartaRestaurante).filter(CartaRestaurante.categoria == categoria[0]).count()
            platos_por_categoria[categoria[0]] = count
    
    return CartaStatsResponse(
        total_platos=total_platos,
        platos_fijos=platos_fijos,
        platos_variables=platos_variables,
        platos_activos=platos_activos,
        platos_inactivos=platos_inactivos,
        platos_por_categoria=platos_por_categoria
    )


@router.get("/stats/menus", response_model=MenuStatsResponse)
def get_menu_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtener estadísticas de menús"""
    total_menus = db.query(MenuDia).count()
    menus_activos = db.query(MenuDia).filter(MenuDia.activo == True).count()
    menus_inactivos = db.query(MenuDia).filter(MenuDia.activo == False).count()
    
    # Menú de hoy
    hoy = date.today().strftime('%Y-%m-%d')
    menu_hoy = db.query(MenuDia).filter(
        MenuDia.fecha == hoy,
        MenuDia.activo == True
    ).first()
    
    return MenuStatsResponse(
        total_menus=total_menus,
        menus_activos=menus_activos,
        menus_inactivos=menus_inactivos,
        menu_hoy=menu_hoy
    )


