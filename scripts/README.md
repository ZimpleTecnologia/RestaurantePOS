# Scripts del Sistema POS

Este directorio contiene scripts de utilidad para el Sistema POS.

## 📁 Archivos Disponibles

### 🔧 Scripts de Python

#### `clean_database.py`
**Descripción**: Script principal para limpiar todos los datos de la base de datos.

**Funcionalidades**:
- ✅ Elimina todos los datos de todas las tablas
- ✅ Preserva el usuario administrador (admin)
- ✅ Resetea las secuencias de ID
- ✅ Muestra estadísticas de limpieza
- ✅ Confirmación interactiva de seguridad

**Uso**:
```bash
# Desde el directorio raíz del proyecto
python scripts/clean_database.py

# Desde el directorio scripts
python clean_database.py
```

**Tablas que se limpian**:
- Ventas y transacciones (Sale, SaleItem, Payment, Credit)
- Órdenes y pedidos (Order, OrderItem)
- Inventario y compras (Purchase, PurchaseItem, InventoryMovement)
- Productos y categorías (Product, Category, SubCategory)
- Clientes y proveedores (Customer, Supplier)
- Mesas y ubicaciones (Table, Location)
- Recetas (Recipe, RecipeItem)
- Configuraciones del sistema (SystemSettings)
- Usuarios (excepto admin)

#### `create_admin_user.py`
**Descripción**: Crea usuarios por defecto (admin, vendedor, caja).

**Uso**:
```bash
python scripts/create_admin_user.py
```

**Usuarios creados**:
- **Admin**: `admin` / `admin123`
- **Vendedor**: `vendedor` / `vendedor123`
- **Caja**: `caja` / `caja123`

### 🐚 Scripts de Shell

#### `clean_db.sh`
**Descripción**: Wrapper de shell para ejecutar la limpieza de base de datos.

**Opciones**:
- `-h, --help`: Mostrar ayuda
- `-f, --force`: Ejecutar sin verificar contenedores
- `-y, --yes`: Confirmar automáticamente

**Uso**:
```bash
# Ejecutar con confirmación interactiva
./scripts/clean_db.sh

# Ejecutar sin verificar contenedores
./scripts/clean_db.sh --force

# Confirmar automáticamente
./scripts/clean_db.sh --yes

# Ver ayuda
./scripts/clean_db.sh --help
```

#### `start.sh`
**Descripción**: Script de inicio que espera a que PostgreSQL esté disponible.

**Funcionalidades**:
- ✅ Espera a que PostgreSQL esté listo
- ✅ Ejecuta migraciones automáticamente
- ✅ Crea directorios necesarios
- ✅ Inicia la aplicación FastAPI

#### `check-connection.sh`
**Descripción**: Verifica la conectividad con la base de datos.

### 📊 Directorios

#### `logs/`
Directorio para archivos de log generados por los scripts.

#### `uploads/`
Directorio para archivos subidos temporalmente durante la ejecución de scripts.

## 🚀 Casos de Uso Comunes

### 1. Limpiar Base de Datos para Desarrollo

```bash
# Opción 1: Usando el script de shell (recomendado)
./scripts/clean_db.sh

# Opción 2: Usando Python directamente
python scripts/clean_database.py
```

### 2. Crear Usuarios por Defecto

```bash
python scripts/create_admin_user.py
```

### 3. Verificar Conexión a Base de Datos

```bash
./scripts/check-connection.sh
```

### 4. Iniciar Aplicación con Verificaciones

```bash
./scripts/start.sh
```

## ⚠️ Advertencias Importantes

### Script de Limpieza (`clean_database.py`)

1. **⚠️ IRREVERSIBLE**: La limpieza NO se puede deshacer
2. **💾 Backup**: Siempre haz backup antes de limpiar
3. **🔒 Admin**: El usuario admin se preserva automáticamente
4. **🔄 Secuencias**: Los IDs se resetean para empezar desde 1

### Script de Usuarios (`create_admin_user.py`)

1. **🔄 No Duplica**: No crea usuarios si ya existen
2. **🔑 Contraseñas**: Usa contraseñas por defecto (cambiar en producción)
3. **👥 Roles**: Crea usuarios con roles específicos

## 🔧 Configuración

### Variables de Entorno

Los scripts utilizan las mismas variables de entorno que la aplicación principal:

```bash
# Base de datos
DATABASE_URL=postgresql://sistema_pos_user:sistema_pos_password@postgres:5432/sistema_pos

# Seguridad
SECRET_KEY=tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion

# Aplicación
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Docker

Los scripts están diseñados para funcionar tanto en:
- **Entorno local**: Con Python instalado directamente
- **Contenedores Docker**: Con la aplicación ejecutándose en Docker

## 📝 Logs y Debugging

### Habilitar Logs Detallados

```bash
# Para scripts Python
export PYTHONPATH=/app
python -u scripts/clean_database.py

# Para scripts shell
bash -x scripts/clean_db.sh
```

### Verificar Estado de Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it sistema_pos_db psql -U sistema_pos_user -d sistema_pos

# Verificar tablas
\dt

# Contar registros
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM sales;
```

## 🆘 Solución de Problemas

### Error: "No se pudo conectar a la base de datos"

1. Verificar que Docker esté ejecutándose
2. Verificar que los contenedores estén activos:
   ```bash
   docker ps | grep sistema_pos
   ```
3. Verificar variables de entorno
4. Ejecutar script de verificación:
   ```bash
   ./scripts/check-connection.sh
   ```

### Error: "Permission denied"

1. Hacer ejecutable el script:
   ```bash
   chmod +x scripts/clean_db.sh
   ```

### Error: "Module not found"

1. Verificar PYTHONPATH:
   ```bash
   export PYTHONPATH=/app
   ```
2. Ejecutar desde el directorio raíz del proyecto

## 📞 Soporte

Para problemas con los scripts:

1. Verificar logs en `scripts/logs/`
2. Ejecutar con modo debug
3. Verificar configuración de base de datos
4. Revisar documentación de la aplicación principal
