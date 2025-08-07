# Sistema POS - Guía de Instalación Rápida

Un sistema completo de punto de venta desarrollado con FastAPI, PostgreSQL y Bootstrap.

## 🚀 Instalación Rápida

### 1. Prerrequisitos
- Python 3.8+
- PostgreSQL 12+
- Git

### 2. Clonar y configurar
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd SistemaPOS

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar base de datos
```bash
# Crear base de datos PostgreSQL
psql -U postgres
CREATE DATABASE sistema_pos;
CREATE USER sistema_pos_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE sistema_pos TO sistema_pos_user;
\q
```

### 4. Configurar variables de entorno
```bash
# Copiar archivo de configuración
cp env.example .env

# Editar .env con tus datos:
# DATABASE_URL=postgresql://sistema_pos_user:tu_password@localhost:5432/sistema_pos
# SECRET_KEY=tu-clave-secreta-aqui
```

### 5. Inicializar base de datos
```bash
# Crear tablas
python -c "from app.database import create_tables; create_tables()"

# Crear usuario administrador
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
print('✅ Usuario admin creado: admin / admin123')
"
```

### 6. Ejecutar aplicación
```bash
# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Acceso
- **Aplicación**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Usuario**: admin
- **Contraseña**: admin123

## 🖨️ Funcionalidades Principales

### Gestión de Ventas
- Crear y gestionar ventas
- **Impresión de tickets** con formato profesional
- Vista previa de tickets antes de imprimir
- Cálculo automático de IVA y totales
- Gestión de clientes y productos

### Gestión de Productos
- Catálogo completo de productos
- Control de inventario en tiempo real
- Códigos de barras y precios
- Categorización y búsqueda

### Gestión de Clientes
- Base de datos de clientes
- Historial de compras
- Información de contacto

### Reportes
- Reportes de ventas diarias, semanales y mensuales
- Análisis de productos más vendidos
- Estadísticas de rendimiento

## 🖨️ Impresión de Tickets

### Características
- **Formato profesional**: Tickets optimizados para impresoras térmicas (80mm)
- **Información completa**: Número de ticket, fecha, cliente, productos, totales
- **Vista previa**: Revisar el ticket antes de imprimir
- **Impresión directa**: Un clic para imprimir desde la interfaz

### Uso
1. Ve a la página de **Ventas**
2. Encuentra la venta que deseas imprimir
3. Haz clic en el botón **Imprimir** (ícono de impresora)
4. Confirma la impresión
5. El ticket se imprimirá automáticamente

### Personalización
- Los estilos se encuentran en `static/css/ticket.css`
- Puedes modificar fuentes, tamaños y formato
- Documentación completa en `docs/PRINTING_TICKETS.md`

## 📋 Comandos Útiles

### Desarrollo
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Ejecutar con recarga automática
uvicorn app.main:app --reload

# Ejecutar en puerto específico
uvicorn app.main:app --port 8080
```

### Base de datos
```bash
# Usar Alembic para migraciones
alembic revision --autogenerate -m "Descripción del cambio"
alembic upgrade head

# Resetear base de datos
alembic downgrade base
alembic upgrade head
```

### Docker (opcional)
```bash
# Construir imagen
docker build -t sistema-pos .

# Ejecutar contenedor
docker run -p 8000:8000 sistema-pos
```

## 🔧 Solución de Problemas

### Error de conexión a PostgreSQL
- Verificar que PostgreSQL esté ejecutándose
- Comprobar credenciales en `.env`
- Verificar que la base de datos existe

### Error de dependencias
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error de puerto ocupado
```bash
# Cambiar puerto
uvicorn app.main:app --port 8080

# O matar proceso en puerto 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

## 📁 Estructura del Proyecto
```
SistemaPOS/
├── app/                    # Código principal
│   ├── main.py            # Punto de entrada
│   ├── models/            # Modelos de BD
│   ├── routers/           # Rutas API
│   └── schemas/           # Validación de datos
├── templates/             # Plantillas HTML
├── static/               # Archivos estáticos
├── requirements.txt      # Dependencias
├── env.example          # Configuración ejemplo
└── README.md           # Este archivo
```

## 🚀 Características Principales

- ✅ **Ventas**: Registro, consulta, múltiples métodos de pago
- ✅ **Inventario**: Control de stock, categorías, lotes
- ✅ **Clientes**: Gestión, créditos, historial
- ✅ **Reportes**: Exportables a Excel/CSV
- ✅ **Multi-usuario**: Roles admin, vendedor, caja
- ✅ **Facturas**: Generación en PDF/HTML

## 📞 Soporte

- **Documentación API**: http://localhost:8000/docs
- **Issues**: Crear en el repositorio
- **Logs**: Revisar consola donde ejecutas uvicorn

---

**¡Listo para usar! 🎉** 