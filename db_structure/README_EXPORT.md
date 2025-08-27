# Exportación de Base de Datos - Sistema POS

Este directorio contiene scripts para exportar la base de datos del Sistema POS desde el contenedor Docker.

## 📁 Archivos Generados

### 1. `db_structure_only.sql`
- **Contenido:** Solo la estructura de la base de datos (tablas, índices, constraints)
- **Uso:** Para crear una base de datos limpia sin datos
- **Tamaño:** Pequeño (solo estructura)

### 2. `db_structure_with_sample_data.sql`
- **Contenido:** Estructura completa + datos de ejemplo
- **Uso:** Para crear una base de datos con datos de prueba
- **Tamaño:** Mediano (estructura + datos)

## 🚀 Scripts Disponibles

### PowerShell (Windows)
```powershell
# Exportar todo (recomendado)
.\export_all.ps1

# Exportar solo estructura
.\export_structure.ps1

# Exportar estructura con datos
.\export_with_sample_data.ps1
```

### Bash (Linux/Mac)
```bash
# Exportar solo estructura
./export_structure.sh

# Exportar estructura con datos
./export_with_sample_data.sh
```

## 📋 Requisitos Previos

1. **Docker Desktop** instalado y corriendo
2. **Contenedor de base de datos** activo:
   ```bash
   docker-compose up -d
   ```
3. **Permisos de ejecución** (Linux/Mac):
   ```bash
   chmod +x *.sh
   ```

## 🔧 Configuración de la Base de Datos

### Detalles del Contenedor:
- **Nombre:** `sistema_pos_db`
- **Base de datos:** `sistema_pos`
- **Usuario:** `sistema_pos_user`
- **Contraseña:** `sistema_pos_password`
- **Puerto:** `5432`

### Configuración en docker-compose.yaml:
```yaml
postgres:
  image: postgres:15
  container_name: sistema_pos_db
  environment:
    POSTGRES_DB: sistema_pos
    POSTGRES_USER: sistema_pos_user
    POSTGRES_PASSWORD: sistema_pos_password
```

## 📊 Estructura de la Base de Datos

### Tablas Principales:
- `users` - Usuarios del sistema
- `locations` - Ubicaciones/sucursales
- `tables` - Mesas del restaurante
- `products` - Productos del menú
- `categories` - Categorías de productos
- `orders` - Órdenes de clientes
- `order_items` - Items de las órdenes
- `sales` - Ventas realizadas
- `customers` - Clientes
- `suppliers` - Proveedores
- `inventory` - Inventario
- `settings` - Configuraciones del sistema

## 🔄 Restauración de Base de Datos

### Restaurar desde archivo SQL:
```bash
# Restaurar solo estructura
docker exec -i sistema_pos_db psql -U sistema_pos_user -d sistema_pos < db_structure_only.sql

# Restaurar estructura con datos
docker exec -i sistema_pos_db psql -U sistema_pos_user -d sistema_pos < db_structure_with_sample_data.sql
```

### Restaurar en nueva base de datos:
```bash
# Crear nueva base de datos
docker exec -i sistema_pos_db psql -U sistema_pos_user -c "CREATE DATABASE sistema_pos_backup;"

# Restaurar en la nueva base de datos
docker exec -i sistema_pos_db psql -U sistema_pos_user -d sistema_pos_backup < db_structure_with_sample_data.sql
```

## ⚠️ Notas Importantes

1. **Backup antes de restaurar:** Siempre haz un backup antes de restaurar
2. **Permisos:** Los scripts usan `--no-owner` y `--no-privileges` para compatibilidad
3. **Codificación:** Los archivos se exportan en UTF-8
4. **Tamaño:** Los archivos pueden ser grandes si hay muchos datos

## 🛠️ Solución de Problemas

### Error: "Contenedor no encontrado"
```bash
# Verificar contenedores activos
docker ps

# Iniciar contenedores si no están corriendo
docker-compose up -d
```

### Error: "Permiso denegado"
```bash
# En Linux/Mac, dar permisos de ejecución
chmod +x *.sh
```

### Error: "Base de datos no existe"
```bash
# Verificar que la base de datos existe
docker exec sistema_pos_db psql -U sistema_pos_user -l
```

## 📞 Soporte

Si tienes problemas con la exportación:
1. Verifica que Docker esté corriendo
2. Confirma que el contenedor `sistema_pos_db` esté activo
3. Revisa los logs del contenedor: `docker logs sistema_pos_db`
