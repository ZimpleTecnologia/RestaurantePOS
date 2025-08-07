# Guía de Despliegue - Sistema POS en VPS con EasyPanel

## 📋 Prerrequisitos

- VPS con Docker instalado
- EasyPanel configurado en el VPS
- **Servicio PostgreSQL independiente configurado en EasyPanel** ✅
- Dominio configurado (opcional pero recomendado)

## 🚀 Paso a Paso del Despliegue

### 1. Preparar la Imagen Docker

#### Opción A: Construir localmente y subir
```bash
# En tu máquina local
cd Zimple/RestaurantePOS

# Dar permisos al script de construcción
chmod +x build-image.sh

# Construir la imagen
./build-image.sh v1.0.0

# Exportar la imagen
docker save restaurante-pos:v1.0.0 > restaurante-pos-v1.0.0.tar

# Subir el archivo .tar a tu VPS
scp restaurante-pos-v1.0.0.tar usuario@tu-vps:/tmp/

# En el VPS, cargar la imagen
docker load < /tmp/restaurante-pos-v1.0.0.tar
```

#### Opción B: Usar un registro de contenedores
```bash
# Construir y etiquetar para tu registro
docker build -t tu-registro/restaurante-pos:v1.0.0 .
docker push tu-registro/restaurante-pos:v1.0.0
```

### 2. Configurar EasyPanel

#### 2.1 Crear la aplicación en EasyPanel

1. **Acceder a EasyPanel**
   - Ir a tu panel de EasyPanel
   - Crear una nueva aplicación

2. **Configurar la aplicación**
   - **Nombre**: `restaurante-pos`
   - **Imagen**: `restaurante-pos:v1.0.0` (si construiste localmente)
   - **Puerto**: `8000`

#### 2.2 Configurar Variables de Entorno

Copiar las variables desde `easypanel-variables.env`:

```env
# Base de datos PostgreSQL - Servicio independiente
DATABASE_URL=postgresql://sistema_pos_user:TU_PASSWORD_AQUI@zimple_postgresql:5432/sistema_pos

# Configuración de seguridad
SECRET_KEY=tu-super-secret-key-muy-largo-y-seguro-aqui
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de la aplicación
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Configuración de archivos
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# CORS - Configurar con tu dominio
ALLOWED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

**⚠️ IMPORTANTE**: 
- Reemplazar `TU_PASSWORD_AQUI` con la contraseña real de tu servicio PostgreSQL
- Generar una `SECRET_KEY` segura usando: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- Configurar `ALLOWED_ORIGINS` con tu dominio real

#### 2.3 Configurar Red

Asegúrate de que tu aplicación esté en la misma red que tu servicio PostgreSQL:
- **Red**: `zimple_default` (o la red donde está tu PostgreSQL)

#### 2.4 Configurar Volúmenes (Opcional)

Para persistencia de datos:
- `./uploads:/app/uploads`
- `./logs:/app/logs`

### 3. Verificar Conexión a Base de Datos

#### 3.1 Verificar que el servicio PostgreSQL esté funcionando
- En EasyPanel, ir a la sección "SERVICIOS"
- Verificar que el servicio `postgresql` esté en estado "Running" (punto verde)

#### 3.2 Verificar credenciales
- Ir a "Credenciales" en tu servicio PostgreSQL
- Verificar que los datos coincidan con tu `DATABASE_URL`:
  - Usuario: `sistema_pos_user`
  - Base de datos: `sistema_pos`
  - Host: `zimple_postgresql`
  - Puerto: `5432`

### 4. Iniciar la Aplicación

1. **Desplegar la aplicación** en EasyPanel
2. **Verificar logs** para asegurar que:
   - La aplicación se conecta correctamente a PostgreSQL
   - Las migraciones se ejecutan sin errores
   - La aplicación inicia correctamente

### 5. Configurar Proxy Inverso (Nginx)

Si usas un dominio personalizado:

```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. Configurar SSL (HTTPS)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

## 🔧 Configuración de Seguridad

### 1. Generar Secret Key Seguro
```bash
# Generar una clave secreta segura
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Configurar Firewall
```bash
# Permitir solo puertos necesarios
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 3. Configurar Backup de Base de Datos
```bash
# Script de backup automático
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump sistema_pos > /backups/sistema_pos_$DATE.sql
```

## 📊 Monitoreo y Logs

### 1. Ver logs de la aplicación
```bash
# En EasyPanel o directamente
docker logs restaurante-pos-container
```

### 2. Monitorear recursos
```bash
# Ver uso de recursos
docker stats restaurante-pos-container
```

### 3. Verificar conectividad entre servicios
```bash
# Desde el contenedor de la aplicación
docker exec -it restaurante-pos-container ping zimple_postgresql
```

## 🔄 Actualizaciones

### 1. Actualizar la aplicación
```bash
# Construir nueva versión
./build-image.sh v1.1.0

# En el VPS, actualizar la imagen
docker pull tu-registro/restaurante-pos:v1.1.0

# Reiniciar el contenedor en EasyPanel
```

### 2. Migraciones de base de datos
```bash
# Ejecutar migraciones si es necesario
docker exec -it restaurante-pos-container alembic upgrade head
```

## 🚨 Troubleshooting

### Problemas comunes:

1. **Error de conexión a BD**
   - Verificar que el servicio PostgreSQL esté ejecutándose
   - Verificar que ambos servicios estén en la misma red
   - Verificar credenciales en `DATABASE_URL`
   - Verificar logs: `docker logs container_name`

2. **Error de permisos**
   - Verificar que los volúmenes tengan permisos correctos
   - Verificar usuario del contenedor

3. **Aplicación no responde**
   - Verificar logs: `docker logs container_name`
   - Verificar health check: `curl http://localhost:8000/health`
   - Verificar que PostgreSQL esté disponible

4. **Error de red entre servicios**
   - Verificar que ambos servicios estén en la misma red Docker
   - Verificar conectividad: `docker exec -it container ping servicio_bd`

## 📞 Soporte

Para problemas específicos:
1. Revisar logs de la aplicación
2. Verificar configuración de variables de entorno
3. Comprobar conectividad de red entre servicios
4. Verificar estado del servicio PostgreSQL en EasyPanel
