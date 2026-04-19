"""
Router de autenticación
"""
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.security import verify_password, create_access_token, get_password_hash
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.auth.dependencies import get_current_user, get_current_active_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario o email ya existe"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Iniciar sesión (formulario)"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Actualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login-json", response_model=Token)
def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión (JSON)"""
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Actualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user 


@router.get("/modulos-visibles")
def get_modulos_visibles(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de módulos de navegación visibles para el usuario actual
    basándose en sus permisos.
    """
    from app.models.user import UserRole
    
    # Refrescar el usuario para asegurar que los permisos estén cargados
    db.refresh(current_user, ["permisos"])
    
    # Mapeo de módulos de navegación a códigos de permisos base
    modulos_navegacion = [
        {"nombre": "Administración", "url": "/admin/administracion", "icono": "bi-shield-lock", "codigos_permisos": ["mesas", "usuarios", "permisos"], "codigo_modulo": "administracion"},
        {"nombre": "Cocina", "url": "/kitchen", "icono": "bi-fire", "codigos_permisos": ["cocina"], "codigo_modulo": "operaciones"},
        {"nombre": "Pedidos a Cocina", "url": "/pedidos/cocina", "icono": "bi-clipboard-check", "codigos_permisos": ["cocina"], "codigo_modulo": "operaciones"},
        {"nombre": "Gestión Menús", "url": "/admin/menus", "icono": "bi-gear", "codigos_permisos": ["meseros"], "codigo_modulo": "operaciones"},
        {"nombre": "Inventario", "url": "/inventory", "icono": "bi-archive", "codigos_permisos": ["inventario"], "codigo_modulo": "almacen"},
        {"nombre": "Meseros", "url": "/meseros/menus", "icono": "bi-person-badge", "codigos_permisos": ["meseros"], "codigo_modulo": "operaciones"},
        {"nombre": "Mis Pedidos", "url": "/pedidos/mesero/estado", "icono": "bi-clipboard-data", "codigos_permisos": ["meseros"], "codigo_modulo": "operaciones"},
        {"nombre": "Pedidos Menú", "url": "/kitchen/menu-orders", "icono": "bi-list-check", "codigos_permisos": ["cocina"], "codigo_modulo": "operaciones"},
        {"nombre": "Recetas", "url": "/recipes", "icono": "bi-book", "codigos_permisos": ["meseros"], "codigo_modulo": "operaciones"},
        {"nombre": "Caja y Ventas", "url": "/caja-ventas", "icono": "bi-cash-coin", "codigos_permisos": ["ventas", "caja"], "codigo_modulo": "financiero"},
        {"nombre": "Reportes", "url": "/reports", "icono": "bi-graph-up", "codigos_permisos": ["reportes"], "codigo_modulo": "reportes"},
        {"nombre": "Configuración", "url": "/settings", "icono": "bi-gear", "codigos_permisos": ["mesas", "usuarios"], "codigo_modulo": "administracion"}
    ]
    
    # Obtener códigos de permisos del usuario
    # Incluso los ADMIN deben tener permisos asignados para ver módulos
    permisos_usuario = {p.codigo for p in current_user.permisos if p.estado}
    
    # Filtrar módulos según permisos
    modulos_visibles = []
    for modulo in modulos_navegacion:
        # Verificar si el usuario tiene al menos uno de los permisos requeridos
        tiene_acceso = any(codigo in permisos_usuario for codigo in modulo["codigos_permisos"])
        if tiene_acceso:
            modulos_visibles.append(modulo)
    
    return {"modulos": modulos_visibles} 