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
from app.routers import auth, products, sales, customers
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
            "customers": "/api/v1/customers"
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