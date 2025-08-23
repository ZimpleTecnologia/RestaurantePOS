# Scripts SQL para Configuración del Sistema POS

Este directorio contiene los scripts SQL necesarios para configurar la tabla de configuración del sistema POS.

## 📁 Archivos Disponibles

### 1. `complete_system_settings.sql` ⭐ **RECOMENDADO**
- **Script completo** que incluye todo lo necesario
- Crea la tabla, inserta datos, crea funciones y triggers
- Incluye ejemplos de uso y verificación
- **Ejecutar este archivo primero**

### 2. `system_settings.sql`
- Script básico para crear la tabla y configuración inicial
- Incluye triggers y comentarios

### 3. `system_settings_data.sql`
- Script para insertar datos de ejemplo
- Incluye funciones útiles y consultas de verificación
- Ejecutar después del script básico

### 4. `system_settings_cleanup.sql`
- Script para eliminar la tabla si necesitas reiniciar
- ⚠️ **ADVERTENCIA**: Elimina todos los datos de configuración

## 🚀 Instrucciones de Uso

### Opción 1: Script Completo (Recomendado)
```sql
-- Conectar a la base de datos PostgreSQL
psql -h localhost -U sistema_pos_user -d sistema_pos -f complete_system_settings.sql
```

### Opción 2: Scripts por Separado
```sql
-- 1. Crear tabla básica
psql -h localhost -U sistema_pos_user -d sistema_pos -f system_settings.sql

-- 2. Insertar datos y funciones
psql -h localhost -U sistema_pos_user -d sistema_pos -f system_settings_data.sql
```

### Opción 3: Desde pgAdmin o DBeaver
1. Abrir el archivo `complete_system_settings.sql`
2. Ejecutar todo el script
3. Verificar los resultados

## 📊 Estructura de la Tabla

La tabla `system_settings` incluye:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | SERIAL | ID único (siempre será 1) |
| `company_name` | VARCHAR(200) | Nombre de la empresa |
| `app_title` | VARCHAR(100) | Título de la aplicación |
| `currency` | VARCHAR(10) | Código de moneda (USD, COP, etc.) |
| `timezone` | VARCHAR(50) | Zona horaria |
| `primary_color` | VARCHAR(7) | Color primario del tema |
| `secondary_color` | VARCHAR(7) | Color secundario del tema |
| `accent_color` | VARCHAR(7) | Color de acento |
| `sidebar_color` | VARCHAR(7) | Color del sidebar |
| `print_header` | TEXT | Encabezado para tickets |
| `print_footer` | TEXT | Pie de página para tickets |
| `enable_notifications` | BOOLEAN | Habilitar notificaciones |
| `low_stock_threshold` | INTEGER | Umbral de stock bajo |

## 🎨 Temas Predefinidos

El sistema incluye 5 temas predefinidos:

1. **Azul Clásico** (por defecto)
   - Primario: `#667eea`
   - Secundario: `#764ba2`

2. **Verde Naturaleza**
   - Primario: `#28a745`
   - Secundario: `#20c997`

3. **Naranja Energía**
   - Primario: `#fd7e14`
   - Secundario: `#e83e8c`

4. **Rojo Pasión**
   - Primario: `#dc3545`
   - Secundario: `#fd7e14`

5. **Púrpura Elegante**
   - Primario: `#6f42c1`
   - Secundario: `#e83e8c`

## 💱 Monedas Soportadas

- **USD** - Dólar Estadounidense
- **EUR** - Euro
- **MXN** - Peso Mexicano
- **COP** - Peso Colombiano ⭐
- **ARS** - Peso Argentino
- **CLP** - Peso Chileno
- **PEN** - Sol Peruano
- **BRL** - Real Brasileño

## 🔧 Funciones Útiles

### Obtener Configuración
```sql
SELECT * FROM get_system_config();
```

### Cambiar Moneda
```sql
SELECT update_system_config(p_currency := 'COP');
```

### Cambiar Tema
```sql
SELECT update_system_config(
    p_primary_color := '#28a745',
    p_secondary_color := '#20c997',
    p_accent_color := '#ffc107',
    p_sidebar_color := '#28a745'
);
```

### Cambiar Nombre de Empresa
```sql
SELECT update_system_config(p_company_name := 'Mi Restaurante');
```

## ✅ Verificación

Después de ejecutar el script, verifica que todo funcione:

```sql
-- Verificar que la tabla existe
SELECT COUNT(*) FROM system_settings;

-- Verificar configuración actual
SELECT * FROM get_system_config();

-- Verificar funciones
SELECT update_system_config(p_currency := 'COP');
SELECT * FROM get_system_config();
```

## 🐛 Solución de Problemas

### Error: "relation does not exist"
- Ejecuta primero el script `complete_system_settings.sql`

### Error: "function does not exist"
- Verifica que ejecutaste todo el script completo

### Error: "duplicate key value"
- La tabla ya existe, puedes usar el script de limpieza primero

### Error de permisos
- Asegúrate de que el usuario tenga permisos de CREATE, INSERT, UPDATE

## 📝 Notas Importantes

1. **Siempre hay un solo registro** en la tabla (ID = 1)
2. **Los cambios se aplican inmediatamente** en la aplicación
3. **Los colores deben estar en formato hexadecimal** (#RRGGBB)
4. **La configuración se guarda automáticamente** con timestamps
5. **Puedes personalizar más campos** según tus necesidades

## 🔄 Reiniciar Configuración

Si necesitas reiniciar toda la configuración:

```sql
-- Ejecutar script de limpieza
psql -h localhost -U sistema_pos_user -d sistema_pos -f system_settings_cleanup.sql

-- Ejecutar script completo nuevamente
psql -h localhost -U sistema_pos_user -d sistema_pos -f complete_system_settings.sql
```

## 📞 Soporte

Si tienes problemas con los scripts:

1. Verifica la conexión a la base de datos
2. Asegúrate de tener permisos suficientes
3. Revisa los logs de PostgreSQL
4. Ejecuta los scripts en orden

---

**¡Listo!** Tu sistema POS ahora tiene una configuración personalizable completa. 🎉
