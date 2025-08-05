# Sistema POS - Punto de Venta

Un sistema completo de punto de venta desarrollado con FastAPI, PostgreSQL y Bootstrap. Diseñado para ser escalable, modular y fácil de usar.

## 🚀 Características

### 🔹 VENTAS
- ✅ Registro y consulta de ventas
- ✅ Multiusuarios: administrador, vendedores, cajas
- ✅ Plan separe (créditos)
- ✅ Control de deudas
- ✅ Gestión de domicilios, propinas y comisiones
- ✅ Informes de comisiones por ventas
- ✅ Cierre de caja, devoluciones, edición de ventas
- ✅ Múltiples métodos de pago: Nequi, Daviplata, Efectivo, Addi, Sisticrédito, Rappi, Didi, Food, Transferencias
- ✅ Facturas personalizadas en PDF o HTML
- ✅ Generación de informes exportables (Excel o CSV)

### 🔹 INVENTARIO
- ✅ Entradas y salidas de productos
- ✅ Ingreso de compras
- ✅ Informes de utilidad, productos agotados o menos vendidos
- ✅ Gestión de lotes y fechas de vencimiento
- ✅ Categorías/subcategorías
- ✅ Productos con foto

### 🔹 CLIENTES
- ✅ Registro y gestión de clientes
- ✅ Créditos, abonos, deudas, historial completo

### 🔹 UBICACIONES (RESTAURANTES / SERVICIOS)
- ✅ Control de mesas y ubicaciones
- ✅ Paquetes, combos, recetas de productos

### 🔹 PROVEEDORES
- ✅ Historial de compras, pagos, abonos
- ✅ Informes filtrables por fechas

## 🛠️ Tecnologías Utilizadas

- **Backend**: FastAPI (Python)
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy
- **Autenticación**: JWT
- **Frontend**: HTML + Bootstrap + JavaScript
- **Templates**: Jinja2
- **Migraciones**: Alembic

## 📋 Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd SistemaPOS
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos PostgreSQL

Crear una base de datos PostgreSQL:
```sql
CREATE DATABASE sistema_pos;
CREATE USER sistema_pos_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE sistema_pos TO sistema_pos_user;
```

### 5. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar:
```bash
cp env.example .env
```

Editar `.env` con tus configuraciones:
```env
# Database Configuration
DATABASE_URL=postgresql://sistema_pos_user:tu_password@localhost:5432/sistema_pos

# Security
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 6. Inicializar la base de datos

```bash
# Crear las tablas
python -c "from app.database import create_tables; create_tables()"

# O usar Alembic para migraciones (recomendado)
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 7. Crear usuario administrador

```bash
python -c "
from app.database import SessionLocal
from app.models.user import User
from app.auth.security import get_password_hash

db = SessionLocal()
admin_user = User(
    username='admin',
    email='admin@sistema.com',
    full_name='Administrador',
    hashed_password=get_password_hash('admin123'),
    role='admin',
    is_active=True,
    is_verified=True
)
db.add(admin_user)
db.commit()
db.close()
print('Usuario administrador creado: admin / admin123')
"
```

### 8. Ejecutar la aplicación

```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O usando el script principal
python -m app.main
```

## 🌐 Acceso a la aplicación

- **Aplicación Web**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

## 📱 Uso del Sistema

### Iniciar Sesión
1. Acceder a http://localhost:8000
2. Usar las credenciales:
   - Usuario: `admin`
   - Contraseña: `admin123`

### Funcionalidades Principales

#### Dashboard
- Vista general de estadísticas
- Ventas del día
- Productos con stock bajo
- Gráficos de ventas

#### Ventas
- Crear nueva venta
- Agregar productos
- Seleccionar métodos de pago
- Generar facturas

#### Productos
- Gestionar catálogo de productos
- Categorías y subcategorías
- Control de stock
- Imágenes de productos

#### Clientes
- Registro de clientes
- Gestión de créditos
- Historial de compras
- Reportes de deudas

## 🔧 Configuración para Producción

### 1. Configurar Nginx (opcional)

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Configurar Systemd (opcional)

Crear `/etc/systemd/system/sistema-pos.service`:
```ini
[Unit]
Description=Sistema POS
After=network.target

[Service]
User=www-data
WorkingDirectory=/ruta/a/SistemaPOS
Environment="PATH=/ruta/a/SistemaPOS/venv/bin"
ExecStart=/ruta/a/SistemaPOS/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Variables de entorno para producción

```env
DEBUG=False
SECRET_KEY=clave-super-secreta-y-compleja
DATABASE_URL=postgresql://usuario:password@localhost:5432/sistema_pos
```

## 📊 Estructura del Proyecto

```
SistemaPOS/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal
│   ├── config.py            # Configuraciones
│   ├── database.py          # Configuración de BD
│   ├── auth/                # Autenticación
│   │   ├── __init__.py
│   │   ├── security.py      # JWT y hash
│   │   └── dependencies.py  # Dependencias de auth
│   ├── models/              # Modelos de BD
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── sale.py
│   │   ├── customer.py
│   │   ├── supplier.py
│   │   ├── location.py
│   │   ├── inventory.py
│   │   └── recipe.py
│   ├── schemas/             # Esquemas Pydantic
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── sale.py
│   │   ├── customer.py
│   │   ├── supplier.py
│   │   └── location.py
│   └── routers/             # Rutas de la API
│       ├── __init__.py
│       ├── auth.py
│       ├── products.py
│       ├── sales.py
│       └── customers.py
├── templates/               # Templates HTML
│   ├── base.html
│   └── index.html
├── static/                  # Archivos estáticos
├── alembic/                 # Migraciones
├── requirements.txt         # Dependencias
├── env.example             # Variables de entorno
├── alembic.ini             # Configuración Alembic
└── README.md               # Este archivo
```

## 🔒 Seguridad

- Autenticación JWT
- Hash de contraseñas con bcrypt
- Validación de datos con Pydantic
- CORS configurado
- Roles de usuario (admin, vendedor, caja)

## 📈 Escalabilidad

- Arquitectura modular
- Separación de responsabilidades
- API RESTful
- Base de datos relacional
- Preparado para microservicios

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisar la documentación de la API en `/docs`
2. Verificar los logs de la aplicación
3. Crear un issue en el repositorio

## 🚀 Despliegue en VPS

### DigitalOcean

1. Crear un Droplet Ubuntu
2. Instalar Python, PostgreSQL, Nginx
3. Clonar el repositorio
4. Seguir los pasos de instalación
5. Configurar Nginx como proxy reverso
6. Configurar SSL con Let's Encrypt

### Docker (opcional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

**¡El Sistema POS está listo para usar! 🎉** 