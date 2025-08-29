"""
Aplicación principal del Sistema POS
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.config import settings
from app.database import create_tables
from app.routers import auth, products, sales, customers, inventory, cash_register, settings, orders, tables, notifications, reports, kitchen, caja_ventas
from app.models import *  # Importar todos los modelos para crear las tablas

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema POS",
    description="Sistema de Punto de Venta completo con gestión de inventario, ventas, clientes y más",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Incluir routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(cash_register.router, prefix="/api/v1")
app.include_router(caja_ventas.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(tables.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(kitchen.router, prefix="/api/v1")


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


@app.get("/sales", response_class=HTMLResponse)
async def sales_page(request: Request):
    """Página de ventas"""
    return templates.TemplateResponse("sales.html", {"request": request})


@app.get("/products", response_class=HTMLResponse)
async def products_page(request: Request):
    """Página de productos"""
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/customers", response_class=HTMLResponse)
async def customers_page(request: Request):
    """Página de clientes"""
    return templates.TemplateResponse("customers.html", {"request": request})


@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    """Página de inventario"""
    return templates.TemplateResponse("inventory.html", {"request": request})


@app.get("/tables", response_class=HTMLResponse)
async def tables_page(request: Request):
    """Página de gestión de mesas"""
    return templates.TemplateResponse("tables.html", {"request": request})


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


@app.get("/waiters/orders", response_class=HTMLResponse)
async def waiters_orders_page(request: Request):
    """Página de pedidos para meseros"""
    return templates.TemplateResponse("waiters/orders.html", {"request": request})


@app.get("/kitchen", response_class=HTMLResponse)
async def kitchen_page(request: Request):
    """Página para cocina"""
    return templates.TemplateResponse("kitchen/index.html", {"request": request})


@app.get("/test-kitchen", response_class=HTMLResponse)
async def test_kitchen_page(request: Request):
    """Página de prueba para cocina"""
    return templates.TemplateResponse("test_kitchen_simple.html", {"request": request})


@app.get("/kitchen-simple", response_class=HTMLResponse)
async def kitchen_simple_page(request: Request):
    """Página simple de cocina para debug"""
    return templates.TemplateResponse("kitchen_simple.html", {"request": request})


# Acciones rápidas
@app.get("/sales/new", response_class=HTMLResponse)
async def new_sale_page(request: Request):
    """Página de nueva venta"""
    return templates.TemplateResponse("sales.html", {"request": request})


@app.get("/products/new", response_class=HTMLResponse)
async def new_product_page(request: Request):
    """Página de nuevo producto"""
    return templates.TemplateResponse("products.html", {"request": request})


@app.get("/customers/new", response_class=HTMLResponse)
async def new_customer_page(request: Request):
    """Página de nuevo cliente"""
    return templates.TemplateResponse("customers.html", {"request": request})


@app.get("/inventory/adjust", response_class=HTMLResponse)
async def adjust_inventory_page(request: Request):
    """Página de ajuste de inventario"""
    return templates.TemplateResponse("inventory.html", {"request": request})


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
            "sales": "/api/v1/sales",
            "customers": "/api/v1/customers",
            "inventory": "/api/v1/inventory",
            "settings": "/api/v1/settings"
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
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 