"""
Router para el sistema de menús del restaurante
Gestión de menús del día con categorías, platos fijos y acompañamientos
"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.database import get_db
from app.models.restaurant_menu import (
    CategoriaMenuRestaurante, PlatoRestaurante, MenuDia, MenuCategoriaPlato, AcompanamientoFijo
)
from app.schemas.restaurant_menu import (
    CategoriaMenuCreate, CategoriaMenuUpdate, CategoriaMenuResponse, CategoriaMenuListResponse,
    PlatoRestauranteCreate, PlatoRestauranteUpdate, PlatoRestauranteResponse, PlatoRestauranteListResponse,
    MenuDiaCreate, MenuDiaUpdate, MenuDiaResponse, MenuDiaListResponse,
    AcompanamientoFijoCreate, AcompanamientoFijoUpdate, AcompanamientoFijoResponse, AcompanamientoFijoListResponse,
    MenuDelDiaCompleto, PedidoMenuDia
)

router = APIRouter(prefix="/restaurant-menu", tags=["menú restaurante"])


# ============================================================================
# ENDPOINTS PARA CATEGORÍAS
# ============================================================================

@router.get("/categorias/", response_model=CategoriaMenuListResponse)
def get_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de categorías de menú"""
    try:
        query = db.query(CategoriaMenuRestaurante)
        
        if activo is not None:
            query = query.filter(CategoriaMenuRestaurante.is_active == activo)
        
        total = query.count()
        categorias_orm = query.order_by(CategoriaMenuRestaurante.orden, CategoriaMenuRestaurante.nombre).offset(skip).limit(limit).all()
        
        # Convertir usando el método personalizado
        categorias = [CategoriaMenuResponse.from_orm(cat) for cat in categorias_orm]
        
        return CategoriaMenuListResponse(categorias=categorias, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/categorias/", response_model=CategoriaMenuResponse)
def create_categoria(categoria: CategoriaMenuCreate, db: Session = Depends(get_db)):
    """Crear nueva categoría de menú"""
    # Verificar que no exista una categoría con el mismo nombre
    existing = db.query(CategoriaMenuRestaurante).filter(CategoriaMenuRestaurante.nombre == categoria.nombre).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una categoría con el nombre '{categoria.nombre}'"
        )
    
    db_categoria = CategoriaMenuRestaurante(**categoria.dict())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    
    return db_categoria


@router.put("/categorias/{categoria_id}", response_model=CategoriaMenuResponse)
def update_categoria(
    categoria_id: int,
    categoria: CategoriaMenuUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar categoría de menú"""
    db_categoria = db.query(CategoriaMenuRestaurante).filter(CategoriaMenuRestaurante.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar nombre único si se está cambiando
    if categoria.nombre and categoria.nombre != db_categoria.nombre:
        existing = db.query(CategoriaMenuRestaurante).filter(
            CategoriaMenuRestaurante.nombre == categoria.nombre,
            CategoriaMenuRestaurante.id != categoria_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una categoría con el nombre '{categoria.nombre}'"
            )
    
    for field, value in categoria.dict(exclude_unset=True).items():
        setattr(db_categoria, field, value)
    
    db_categoria.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_categoria)
    
    return db_categoria


@router.delete("/categorias/{categoria_id}")
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Desactivar categoría de menú"""
    db_categoria = db.query(CategoriaMenuRestaurante).filter(CategoriaMenuRestaurante.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    db_categoria.activo = False
    db_categoria.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Categoría desactivada exitosamente"}


# ============================================================================
# ENDPOINTS PARA PLATOS DEL RESTAURANTE
# ============================================================================

@router.get("/platos/", response_model=PlatoRestauranteListResponse)
def get_platos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tipo: Optional[str] = Query(None, pattern=r'^(Menu_Dia|Plato_Fijo|Acompanamiento_Fijo)$'),
    activo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de platos del restaurante"""
    query = db.query(PlatoRestaurante)
    
    if tipo:
        query = query.filter(PlatoRestaurante.tipo == tipo)
    if activo is not None:
        query = query.filter(PlatoRestaurante.activo == activo)
    
    total = query.count()
    platos_orm = query.order_by(PlatoRestaurante.nombre).offset(skip).limit(limit).all()
    
    # Convertir usando el método personalizado
    platos = [PlatoRestauranteResponse.from_orm(plato) for plato in platos_orm]
    
    return PlatoRestauranteListResponse(platos=platos, total=total)


@router.post("/platos/", response_model=PlatoRestauranteResponse)
def create_plato(plato: PlatoRestauranteCreate, db: Session = Depends(get_db)):
    """Crear nuevo plato del restaurante"""
    db_plato = PlatoRestaurante(**plato.dict())
    db.add(db_plato)
    db.commit()
    db.refresh(db_plato)
    
    return db_plato


@router.put("/platos/{plato_id}", response_model=PlatoRestauranteResponse)
def update_plato(
    plato_id: int,
    plato: PlatoRestauranteUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar plato del restaurante"""
    db_plato = db.query(PlatoRestaurante).filter(PlatoRestaurante.id == plato_id).first()
    if not db_plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    for field, value in plato.dict(exclude_unset=True).items():
        setattr(db_plato, field, value)
    
    db_plato.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_plato)
    
    return db_plato


@router.delete("/platos/{plato_id}")
def delete_plato(plato_id: int, db: Session = Depends(get_db)):
    """Desactivar plato del restaurante"""
    db_plato = db.query(PlatoRestaurante).filter(PlatoRestaurante.id == plato_id).first()
    if not db_plato:
        raise HTTPException(status_code=404, detail="Plato no encontrado")
    
    db_plato.activo = False
    db_plato.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Plato desactivado exitosamente"}


# ============================================================================
# ENDPOINTS PARA MENÚS DEL DÍA
# ============================================================================

@router.get("/menus/", response_model=MenuDiaListResponse)
def get_menus(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activo: Optional[bool] = None,
    publicado: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de menús del día"""
    query = db.query(MenuDia)
    
    # Filtrar por estado (mapear activo/publicado a estado)
    if activo is not None:
        if activo:
            query = query.filter(MenuDia.estado == 'ACTIVE')
        else:
            query = query.filter(MenuDia.estado != 'ACTIVE')
    if publicado is not None:
        if publicado:
            query = query.filter(MenuDia.estado == 'ACTIVE')
        else:
            query = query.filter(MenuDia.estado != 'ACTIVE')
    
    total = query.count()
    menus_orm = query.order_by(MenuDia.fecha.desc()).offset(skip).limit(limit).all()
    
    # Convertir usando el método personalizado
    menus = [MenuDiaResponse.from_orm(menu) for menu in menus_orm]
    
    return MenuDiaListResponse(menus=menus, total=total)


@router.get("/menus/hoy", response_model=MenuDelDiaCompleto)
def get_menu_hoy(db: Session = Depends(get_db)):
    """Obtener menú del día actual completo para meseros"""
    today = date.today()
    
    # Buscar menú del día
    menu = db.query(MenuDia).filter(
        MenuDia.fecha == today,
        MenuDia.estado == 'ACTIVE'
    ).first()
    
    if not menu:
        # Si no hay menú, devolver estructura vacía en lugar de error 404
        return {
            "menu": None,
            "categorias": {},
            "acompanamientos_fijos": [],
            "platos_fijos": [],
            "mensaje": "No hay menú publicado para hoy"
        }
    
    # Obtener platos organizados por categoría (simplificado)
    categorias_platos = {}
    # Por ahora, devolver categorías vacías hasta que se implemente la tabla de relaciones
    
    # Obtener acompañamientos fijos
    acompanamientos = db.query(AcompanamientoFijo).filter(AcompanamientoFijo.activo == True).order_by(AcompanamientoFijo.orden).all()
    
    # Obtener platos fijos
    platos_fijos = db.query(PlatoRestaurante).filter(
        PlatoRestaurante.tipo == 'Plato_Fijo',
        PlatoRestaurante.activo == True
    ).order_by(PlatoRestaurante.nombre).all()
    
    return MenuDelDiaCompleto(
        menu=MenuDiaResponse.from_orm(menu),
        categorias=categorias_platos,
        acompanamientos_fijos=[AcompanamientoFijoResponse.from_orm(a) for a in acompanamientos],
        platos_fijos=[PlatoRestauranteResponse.from_orm(p) for p in platos_fijos]
    )


@router.post("/menus/", response_model=MenuDiaResponse)
def create_menu(menu: MenuDiaCreate, db: Session = Depends(get_db)):
    """Crear nuevo menú del día"""
    # Verificar que no exista menú para la misma fecha
    existing = db.query(MenuDia).filter(MenuDia.fecha == menu.fecha).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un menú para la fecha {menu.fecha}"
        )
    
    # Crear el menú
    menu_data = menu.dict(exclude={'categorias_platos'})
    db_menu = MenuDia(**menu_data)
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    
    # Agregar platos por categoría
    for categoria_nombre, platos_ids in menu.categorias_platos.items():
        # Buscar la categoría
        categoria = db.query(CategoriaMenuRestaurante).filter(CategoriaMenuRestaurante.nombre == categoria_nombre).first()
        if not categoria:
            raise HTTPException(
                status_code=400,
                detail=f"Categoría '{categoria_nombre}' no encontrada"
            )
        
        # Agregar platos a la categoría
        for plato_id in platos_ids:
            # Verificar que el plato existe y es de tipo Menu_Dia
            plato = db.query(PlatoRestaurante).filter(
                PlatoRestaurante.id == plato_id,
                PlatoRestaurante.tipo == 'Menu_Dia',
                PlatoRestaurante.activo == True
            ).first()
            if not plato:
                raise HTTPException(
                    status_code=400,
                    detail=f"Plato con ID {plato_id} no encontrado o no es válido para menú del día"
                )
            
            # Crear relación
            mcp = MenuCategoriaPlato(
                menu_dia_id=db_menu.id,
                categoria_id=categoria.id,
                plato_id=plato_id
            )
            db.add(mcp)
    
    db.commit()
    return db_menu


@router.put("/menus/{menu_id}/publicar")
def publicar_menu(menu_id: int, db: Session = Depends(get_db)):
    """Publicar menú del día para que sea visible para meseros"""
    menu = db.query(MenuDia).filter(MenuDia.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    
    menu.publicado = True
    menu.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Menú publicado exitosamente"}


@router.put("/menus/{menu_id}/despublicar")
def despublicar_menu(menu_id: int, db: Session = Depends(get_db)):
    """Despublicar menú del día"""
    menu = db.query(MenuDia).filter(MenuDia.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    
    menu.publicado = False
    menu.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Menú despublicado exitosamente"}


# ============================================================================
# ENDPOINTS PARA ACOMPAÑAMIENTOS FIJOS
# ============================================================================

@router.get("/acompanamientos/", response_model=AcompanamientoFijoListResponse)
def get_acompanamientos(db: Session = Depends(get_db)):
    """Obtener lista de acompañamientos fijos"""
    acompanamientos_orm = db.query(AcompanamientoFijo).filter(
        AcompanamientoFijo.activo == True
    ).order_by(AcompanamientoFijo.orden, AcompanamientoFijo.nombre).all()
    
    # Convertir usando el método personalizado
    acompanamientos = [AcompanamientoFijoResponse.from_orm(acompanamiento) for acompanamiento in acompanamientos_orm]
    
    return AcompanamientoFijoListResponse(acompanamientos=acompanamientos, total=len(acompanamientos))


@router.post("/acompanamientos/", response_model=AcompanamientoFijoResponse)
def create_acompanamiento(acompanamiento: AcompanamientoFijoCreate, db: Session = Depends(get_db)):
    """Crear nuevo acompañamiento fijo"""
    db_acompanamiento = AcompanamientoFijo(**acompanamiento.dict())
    db.add(db_acompanamiento)
    db.commit()
    db.refresh(db_acompanamiento)
    
    return db_acompanamiento


@router.put("/acompanamientos/{acompanamiento_id}", response_model=AcompanamientoFijoResponse)
def update_acompanamiento(
    acompanamiento_id: int,
    acompanamiento: AcompanamientoFijoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar acompañamiento fijo"""
    db_acompanamiento = db.query(AcompanamientoFijo).filter(AcompanamientoFijo.id == acompanamiento_id).first()
    if not db_acompanamiento:
        raise HTTPException(status_code=404, detail="Acompañamiento no encontrado")
    
    for field, value in acompanamiento.dict(exclude_unset=True).items():
        setattr(db_acompanamiento, field, value)
    
    db_acompanamiento.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_acompanamiento)
    
    return db_acompanamiento


@router.delete("/acompanamientos/{acompanamiento_id}")
def delete_acompanamiento(acompanamiento_id: int, db: Session = Depends(get_db)):
    """Desactivar acompañamiento fijo"""
    db_acompanamiento = db.query(AcompanamientoFijo).filter(AcompanamientoFijo.id == acompanamiento_id).first()
    if not db_acompanamiento:
        raise HTTPException(status_code=404, detail="Acompañamiento no encontrado")
    
    db_acompanamiento.activo = False
    db_acompanamiento.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Acompañamiento desactivado exitosamente"}
