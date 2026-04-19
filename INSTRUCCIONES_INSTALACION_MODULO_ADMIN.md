# 🚀 Instrucciones de Instalación - Módulo de Administración

## ⚠️ ERROR DETECTADO

El error que recibiste:
```
column users.telefono does not exist
```

Significa que la base de datos no tiene las nuevas tablas y columnas necesarias para el módulo.

---

## ✅ SOLUCIÓN - Ejecutar en este orden:

### **PASO 1: Ejecutar Migraciones** 🔧

Abre tu terminal en la carpeta del proyecto y ejecuta:

```bash
python migrate_admin_module.py
```

**¿Qué hace este script?**
- ✅ Agrega columna `telefono` a la tabla `users`
- ✅ Crea tabla `mesas`
- ✅ Crea tabla `permisos`
- ✅ Crea tabla `usuario_permiso` (relación muchos-a-muchos)
- ✅ Crea índices para optimizar consultas

**Salida esperada:**
```
🚀 Iniciando migraciones del Módulo de Administración...
📝 Ejecutando: Agregar columna telefono...
   ✅ Agregar columna telefono - OK
📝 Ejecutando: Crear tabla mesas...
   ✅ Crear tabla mesas - OK
...
✅ Todas las migraciones completadas exitosamente
```

---

### **PASO 2: Poblar Permisos** 📋

Después de que las migraciones sean exitosas, ejecuta:

```bash
python seed_permisos.py
```

**¿Qué hace este script?**
- ✅ Crea 30 permisos predefinidos
- ✅ Organiza permisos en 5 módulos (administración, operaciones, financiero, almacén, reportes)

**Salida esperada:**
```
🚀 Poblando permisos iniciales...
✅ 30 permisos creados exitosamente
✅ Usuario ADMIN tiene acceso completo automático
✅ Proceso completado
```

---

### **PASO 3: Iniciar la Aplicación** 🎯

```bash
python -m uvicorn app.main:app --reload
```

---

### **PASO 4: Acceder al Módulo** 🌐

Abre tu navegador en:
- **Mesas**: http://localhost:8000/admin/mesas
- **Usuarios**: http://localhost:8000/admin/usuarios
- **Permisos**: http://localhost:8000/admin/permisos
- **API Docs**: http://localhost:8000/docs

---

## 🛠️ Comandos Rápidos (Copiar y Pegar)

```bash
# 1. Ejecutar migraciones
python migrate_admin_module.py

# 2. Poblar permisos
python seed_permisos.py

# 3. Iniciar app
python -m uvicorn app.main:app --reload
```

---

## 📊 Verificación

Para verificar que todo se instaló correctamente, puedes ejecutar estos queries en tu base de datos:

```sql
-- Verificar tabla mesas
SELECT COUNT(*) FROM mesas;

-- Verificar permisos
SELECT COUNT(*) FROM permisos;

-- Verificar columna telefono
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'telefono';

-- Listar permisos por módulo
SELECT modulo, COUNT(*) as total 
FROM permisos 
GROUP BY modulo 
ORDER BY modulo;
```

---

## ❓ Preguntas Frecuentes

### ¿Qué pasa si ejecuto el script de migración dos veces?
✅ **Seguro**: Usa `IF NOT EXISTS` y `ADD COLUMN IF NOT EXISTS`, así que no hay problema.

### ¿Perderé datos existentes?
✅ **No**: Solo agrega nuevas tablas y columnas, no modifica datos existentes.

### ¿Puedo revertir los cambios?
⚠️ No hay script de rollback. Si necesitas revertir:
```sql
DROP TABLE IF EXISTS usuario_permiso CASCADE;
DROP TABLE IF EXISTS permisos CASCADE;
DROP TABLE IF EXISTS mesas CASCADE;
ALTER TABLE users DROP COLUMN IF EXISTS telefono;
```

### ¿Funciona con SQLite?
⚠️ Los scripts están optimizados para PostgreSQL. Para SQLite, necesitarás ajustes menores.

---

## 🆘 Problemas Comunes

### Error: "relation already exists"
✅ **Solución**: Ya está creado, continúa con el siguiente paso.

### Error: "permission denied"
⚠️ **Solución**: Verifica que tu usuario de base de datos tenga permisos para crear tablas.

### Error: "cannot import name..."
⚠️ **Solución**: Asegúrate de estar en el directorio correcto y tener todas las dependencias instaladas.

---

## 📚 Archivos Creados

- ✅ `migrate_admin_module.py` - Script de migración Python
- ✅ `migrate_admin_module.sql` - SQL directo (alternativa)
- ✅ `seed_permisos.py` - Poblador de permisos
- ✅ `add_telefono_column.py` - Migración individual (opcional)
- ✅ `add_telefono_column.sql` - SQL individual (opcional)

---

## 🎉 ¡Listo!

Después de seguir estos pasos, tu módulo de administración estará completamente operativo.

Para más información, consulta: **MODULO_ADMINISTRACION_README.md**

