"""
Aplicación principal del Sistema POS
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import os

from app.config import settings as app_settings
from app.database import create_tables
from app.routers import auth, products, inventory, settings, notifications, reports, kitchen, caja_ventas, waiters, recipes, menu, websocket, carta_restaurante, menus_unified, menus_public_simple, restaurant_menu, test_simple, debug_menus, debug_menus_sql, menu_restructured, menu_restructured_simple, mesas, usuarios, permisos
from app.models import *  # Importar todos los modelos para crear las tablas
from app.middleware import AuthMiddleware, SessionTimeoutMiddleware
from app.middlewares.inventory_access import InventoryAccessMiddleware

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema POS",
    description="Sistema de Punto de Venta completo con gestión de inventario, ventas, clientes y más",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Exception handler para errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler personalizado para errores de validación"""
    errors = exc.errors()
    error_details = []
    for error in errors:
        error_details.append({
            "loc": list(error["loc"]),
            "msg": error["msg"],
            "type": error["type"],
            "input": str(error.get("input", ""))[:100]  # Limitar tamaño para evitar problemas
        })
    print(f"❌ Error de validación en {request.url.path}:")
    print(f"   Errores: {error_details}")
    return JSONResponse(
        status_code=422,
        content={"detail": error_details}
)

# Agregar middlewares de autenticación y timeout
app.add_middleware(AuthMiddleware)
app.add_middleware(SessionTimeoutMiddleware, timeout_minutes=app_settings.access_token_expire_minutes)
app.add_middleware(InventoryAccessMiddleware)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar archivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar archivos de uploads
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Incluir routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(recipes.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(kitchen.router, prefix="/api/v1")
app.include_router(caja_ventas.router, prefix="/api/v1")
app.include_router(waiters.router, prefix="/api/v1")
app.include_router(menu.router, prefix="/api/v1")
app.include_router(websocket.router)
app.include_router(carta_restaurante.router, prefix="/api/v1")
app.include_router(menus_unified.router, prefix="/api/v1")
app.include_router(menus_public_simple.router, prefix="/api/v1")
app.include_router(restaurant_menu.router, prefix="/api/v1")
app.include_router(test_simple.router, prefix="/api/v1")
app.include_router(debug_menus.router, prefix="/api/v1")
app.include_router(debug_menus_sql.router, prefix="/api/v1")
app.include_router(menu_restructured.router, prefix="/api/v1/menu-restructured")
app.include_router(menu_restructured_simple.router, prefix="/api/v1/menu-restructured-simple")

# Routers del Módulo de Administración
app.include_router(mesas.router, prefix="/api/v1")
app.include_router(usuarios.router, prefix="/api/v1")
app.include_router(permisos.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    print("🚀 Iniciando Sistema POS...")
    # Crear tablas si no existen
    create_tables()
    print("✅ Base de datos inicializada")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página principal"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/products", response_class=HTMLResponse)
async def products_page(request: Request):
    """Página de productos"""
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    """Página de inventario"""
    return templates.TemplateResponse("inventory.html", {"request": request})


@app.get("/admin/menus", response_class=HTMLResponse)
async def admin_menus_page(request: Request):
    """Página de administración de menús - Sistema reestructurado"""
    return templates.TemplateResponse("menu_restructured_admin.html", {"request": request})


@app.get("/meseros/menus", response_class=HTMLResponse)
async def mesero_menus_page(request: Request):
    """Página de menú para meseros"""
    return templates.TemplateResponse("menu_mesero.html", {"request": request})



@app.get("/recipes", response_class=HTMLResponse)
async def recipes_page(request: Request):
    """Página de recetas"""
    return templates.TemplateResponse("recipes.html", {"request": request})


@app.get("/waiters", response_class=HTMLResponse)
async def waiters_page(request: Request):
    """Página de meseros"""
    return templates.TemplateResponse("waiters/index.html", {"request": request})


@app.get("/debug-frontend", response_class=HTMLResponse)
async def debug_frontend_page(request: Request):
    """Página de debug del frontend"""
    return templates.TemplateResponse("verificar_frontend.html", {"request": request})


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Página de reportes"""
    return templates.TemplateResponse("reports.html", {"request": request})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Página de configuración"""
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/cash-register", response_class=HTMLResponse)
async def cash_register_page(request: Request):
    """Página del sistema de caja"""
    return templates.TemplateResponse("cash-register.html", {"request": request})


@app.get("/caja-ventas", response_class=HTMLResponse)
async def caja_ventas_page(request: Request):
    """Página del módulo unificado Caja y Ventas"""
    return templates.TemplateResponse("caja-ventas.html", {"request": request})


@app.get("/waiters", response_class=HTMLResponse)
async def waiters_page(request: Request):
    """Página para meseros"""
    return templates.TemplateResponse("waiters/index.html", {"request": request})


@app.get("/kitchen", response_class=HTMLResponse)
async def kitchen_page(request: Request):
    """Página para cocina"""
    return templates.TemplateResponse("kitchen/index.html", {"request": request})


@app.get("/kitchen/menu-orders", response_class=HTMLResponse)
async def kitchen_menu_orders_page(request: Request):
    """Página para cocina - Pedidos del menú"""
    return templates.TemplateResponse("kitchen/menu-orders.html", {"request": request})


@app.get("/kitchen/menu-orders-new", response_class=HTMLResponse)
async def kitchen_menu_orders_new_page(request: Request):
    """Página para cocina - Pedidos del menú (Sistema Reestructurado)"""
    return templates.TemplateResponse("kitchen/menu-orders-new.html", {"request": request})


@app.get("/waiters/menu", response_class=HTMLResponse)
async def waiters_menu_page(request: Request):
    """Página para meseros - Menú del día"""
    return templates.TemplateResponse("waiters/menu.html", {"request": request})


@app.get("/waiters/menu-new", response_class=HTMLResponse)
async def waiters_menu_new_page(request: Request):
    """Página para meseros - Menú del día (Sistema Reestructurado)"""
    return templates.TemplateResponse("waiters/menu-new.html", {"request": request})




@app.get("/products/admin-products", response_class=HTMLResponse)
async def admin_products_page(request: Request):
    """Página de administración de productos"""
    return templates.TemplateResponse("products/admin-products.html", {"request": request})


@app.get("/products/admin-products-separated", response_class=HTMLResponse)
async def admin_products_separated_page(request: Request):
    """Página de administración de productos separados (Carta e Inventario)"""
    return templates.TemplateResponse("products/admin-products-separated.html", {"request": request})


@app.get("/carta-restaurante/admin", response_class=HTMLResponse)
async def carta_restaurante_admin_page(request: Request):
    """Página de administración de Carta Restaurante"""
    return templates.TemplateResponse("carta_restaurante/admin.html", {"request": request})


@app.get("/products/admin-menus", response_class=HTMLResponse)
async def admin_menus_page(request: Request):
    """Página de administración de menús del día"""
    return templates.TemplateResponse("products/admin-menus.html", {"request": request})


@app.get("/module-development", response_class=HTMLResponse)
async def module_development_page(request: Request):
    """Página de módulo en desarrollo"""
    return templates.TemplateResponse("module_development.html", {"request": request})


# ============================================================================
# RUTAS DEL MÓDULO DE ADMINISTRACIÓN
# ============================================================================

@app.get("/admin/administracion", response_class=HTMLResponse)
async def admin_index_page(request: Request):
    """Página principal del módulo de administración"""
    return templates.TemplateResponse("admin/index.html", {"request": request})


@app.get("/admin/mesas", response_class=HTMLResponse)
async def admin_mesas_page(request: Request):
    """Página de administración de mesas"""
    return templates.TemplateResponse("admin/mesas.html", {"request": request})


@app.get("/admin/usuarios", response_class=HTMLResponse)
async def admin_usuarios_page(request: Request):
    """Página de administración de usuarios/meseros"""
    return templates.TemplateResponse("admin/usuarios.html", {"request": request})


@app.get("/admin/permisos", response_class=HTMLResponse)
async def admin_permisos_page(request: Request):
    """Página de administración de permisos"""
    return templates.TemplateResponse("admin/permisos.html", {"request": request})


@app.get("/health")
async def health_check():
    """Verificación de salud de la aplicación"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Sistema POS"
    }


@app.get("/api/v1/")
async def api_info():
    """Información de la API"""
    return {
        "message": "Sistema POS API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "products": "/api/v1/products",
            "inventory": "/api/v1/inventory",
            "recipes": "/api/v1/recipes",
            "settings": "/api/v1/settings",
            "reports": "/api/v1/reports",
            "kitchen": "/api/v1/kitchen",
            "caja_ventas": "/api/v1/caja-ventas",
            "waiters": "/api/v1/waiters",
            "menu": "/api/v1/menu",
            "websocket": "/ws",
            "administracion": {
                "mesas": "/api/v1/mesas",
                "usuarios": "/api/v1/usuarios",
                "permisos": "/api/v1/permisos"
            }
        }
    }

@app.get("/api/v1/test-settings")
async def test_settings():
    """Endpoint de prueba para verificar que las rutas funcionan"""
    return {
        "message": "Settings router está funcionando",
        "status": "ok",
        "endpoints": {
            "get_settings": "/api/v1/settings/",
            "update_settings": "/api/v1/settings/ (PUT)",
            "get_themes": "/api/v1/settings/themes",
            "get_currencies": "/api/v1/settings/currencies",
            "reset_settings": "/api/v1/settings/reset (POST)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.debug
    ) 