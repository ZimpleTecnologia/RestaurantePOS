# 📋 Módulo de Administración - Sistema POS

## 🎯 Descripción General

Módulo completo para la gestión administrativa del Sistema POS, incluyendo:
- ✅ Gestión de Mesas
- ✅ Gestión de Usuarios/Meseros
- ✅ Sistema de Permisos Dinámico

---

## 📁 Estructura de Archivos Creados

### **Backend - Modelos**
```
app/models/
├── mesa.py              # Modelo Mesa
├── permiso.py           # Modelo Permiso y tabla intermedia usuario_permiso
└── user.py              # Actualizado: campo telefono, relación permisos, método tiene_permiso()
```

### **Backend - Schemas**
```
app/schemas/
├── mesa.py              # MesaCreate, MesaUpdate, MesaResponse, MesaListResponse
├── permiso.py           # PermisoCreate, PermisoUpdate, PermisoResponse, AsignarPermisoRequest
└── user.py              # Actualizado: UserPasswordReset, UserListResponse, permisos en respuesta
```

### **Backend - Routers**
```
app/routers/
├── mesas.py             # CRUD completo de mesas
├── usuarios.py          # CRUD completo de usuarios con reseteo de contraseña
└── permisos.py          # CRUD de permisos + asignación/remoción a usuarios
```

### **Backend - Auth/Middlewares**
```
app/auth/
├── permissions.py       # Sistema de verificación de permisos
└── __init__.py          # Actualizado: exporta funciones de permisos
```

### **Frontend - Templates**
```
templates/admin/
├── mesas.html           # UI gestión de mesas
├── usuarios.html        # UI gestión de usuarios con permisos
└── permisos.html        # UI gestión de permisos por módulo
```

### **Scripts y Utilidades**
```
seed_permisos.py         # Script para poblar 30 permisos iniciales
```

### **Configuración**
```
app/main.py              # Actualizado: rutas y routers del módulo integrados
```

---

## 🔗 Endpoints API

### **Mesas** (`/api/v1/mesas`)
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/` | Listar mesas | Usuario activo |
| GET | `/{id}` | Obtener una mesa | Usuario activo |
| POST | `/` | Crear mesa | ADMIN |
| PUT | `/{id}` | Actualizar mesa | ADMIN |
| PATCH | `/{id}/activar` | Activar/Desactivar | ADMIN |
| DELETE | `/{id}` | Eliminar mesa | ADMIN |

### **Usuarios** (`/api/v1/usuarios`)
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/` | Listar usuarios | Usuario activo |
| GET | `/me` | Usuario actual | Usuario activo |
| GET | `/{id}` | Obtener usuario | Usuario activo (propios) / ADMIN (todos) |
| POST | `/` | Crear usuario | ADMIN |
| PUT | `/{id}` | Actualizar usuario | ADMIN |
| PATCH | `/{id}/activar` | Activar/Desactivar | ADMIN |
| POST | `/{id}/reset-password` | Resetear contraseña | ADMIN |
| DELETE | `/{id}` | Eliminar usuario | ADMIN |
| GET | `/roles/disponibles` | Listar roles | Usuario activo |

### **Permisos** (`/api/v1/permisos`)
| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/` | Listar permisos | Usuario activo |
| GET | `/{id}` | Obtener permiso | Usuario activo |
| POST | `/` | Crear permiso | ADMIN |
| PUT | `/{id}` | Actualizar permiso | ADMIN |
| DELETE | `/{id}` | Eliminar permiso | ADMIN |
| GET | `/usuario/{id}` | Permisos de usuario | Usuario activo |
| POST | `/usuario/{id}/asignar` | Asignar permisos | ADMIN |
| DELETE | `/usuario/{id}/remover/{permiso_id}` | Remover permiso | ADMIN |
| GET | `/modulos/` | Listar módulos | Usuario activo |

---

## 🎨 Rutas Frontend

| Ruta | Descripción |
|------|-------------|
| `/admin/mesas` | Gestión de mesas |
| `/admin/usuarios` | Gestión de usuarios/meseros |
| `/admin/permisos` | Gestión de permisos |

---

## 🔐 Sistema de Permisos

### **Funciones de Verificación**

```python
from app.auth import (
    verificar_permiso,              # Requiere UN permiso específico
    verificar_cualquier_permiso,    # Requiere AL MENOS UNO de varios
    verificar_todos_permisos        # Requiere TODOS los permisos
)

# Uso en endpoints
@router.get("/mesas/", dependencies=[Depends(verificar_permiso("mesas"))])
def get_mesas(...):
    ...
```

### **Permisos Predefinidos** (30 en total)

#### **Administración** (10)
- `mesas`, `mesas_crear`, `mesas_editar`, `mesas_eliminar`
- `usuarios`, `usuarios_crear`, `usuarios_editar`, `usuarios_eliminar`
- `permisos`, `permisos_asignar`

#### **Operaciones** (5)
- `meseros`, `meseros_pedidos`
- `cocina`, `cocina_ver_pedidos`, `cocina_actualizar`

#### **Financiero** (6)
- `ventas`, `ventas_crear`, `ventas_anular`
- `caja`, `caja_abrir`, `caja_cerrar`

#### **Almacén** (5)
- `inventario`, `inventario_crear`, `inventario_editar`, `inventario_movimientos`

#### **Reportes** (4)
- `reportes`, `reportes_ventas`, `reportes_inventario`, `reportes_financieros`

---

## 🚀 Instalación y Configuración

### **1. Ejecutar Migraciones de Base de Datos**

**IMPORTANTE**: Antes de usar el módulo, debes ejecutar las migraciones:

```bash
# Opción 1: Script Python (recomendado)
python migrate_admin_module.py

# Opción 2: SQL directo (si tienes acceso a psql)
psql -U tu_usuario -d tu_base_datos -f migrate_admin_module.sql
```

Este script crea:
- ✅ Columna `telefono` en tabla `users`
- ✅ Tabla `mesas`
- ✅ Tabla `permisos`
- ✅ Tabla `usuario_permiso`
- ✅ Índices para optimización

### **2. Poblar Permisos Iniciales**

Después de ejecutar las migraciones:

```bash
python seed_permisos.py
```

Esto crea 30 permisos predefinidos organizados en 5 módulos.

### **3. Iniciar la Aplicación**

```bash
python -m uvicorn app.main:app --reload
```

### **4. Acceder al Módulo**

```
http://localhost:8000/admin/mesas
http://localhost:8000/admin/usuarios
http://localhost:8000/admin/permisos
```

### **Orden de ejecución**
```bash
# 1. Ejecutar migraciones
python migrate_admin_module.py

# 2. Poblar permisos
python seed_permisos.py

# 3. Iniciar app
python -m uvicorn app.main:app --reload
```

---

## 💡 Ejemplos de Uso

### **Proteger Endpoint con Permiso**

```python
from app.auth import verificar_permiso
from fastapi import Depends

@router.get("/ventas/", dependencies=[Depends(verificar_permiso("ventas"))])
def get_ventas(db: Session = Depends(get_db)):
    # Solo usuarios con permiso "ventas" pueden acceder
    ...
```

### **Verificar Permiso en Modelo User**

```python
if current_user.tiene_permiso("caja_cerrar"):
    # Realizar acción
    ...
```

### **Asignar Permisos desde Frontend**

1. Ir a `/admin/usuarios`
2. Click en botón "Permisos" (🔑 icono) del usuario
3. Marcar/desmarcar checkboxes de permisos
4. Los cambios se guardan automáticamente

---

## 📊 Diagramas

### **Modelo de Datos**

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│    User     │         │ usuario_permiso  │         │   Permiso   │
├─────────────┤         ├──────────────────┤         ├─────────────┤
│ id          │────────>│ usuario_id   (FK)│<────────│ id          │
│ username    │         │ permiso_id   (FK)│         │ codigo      │
│ email       │         │ created_at       │         │ nombre      │
│ full_name   │         └──────────────────┘         │ descripcion │
│ telefono    │                                      │ modulo      │
│ role        │                                      │ estado      │
│ ...         │                                      └─────────────┘
└─────────────┘

┌─────────────┐
│    Mesa     │
├─────────────┤
│ id          │
│ nombre      │
│ numero      │
│ capacidad   │
│ estado      │
└─────────────┘
```

---

## ✅ Checklist de Funcionalidades

### **Mesas**
- [x] Crear mesas
- [x] Listar y filtrar mesas
- [x] Editar mesas
- [x] Activar/Desactivar mesas
- [x] Eliminar mesas
- [x] Estadísticas en dashboard

### **Usuarios**
- [x] Crear usuarios/meseros
- [x] Listar y buscar usuarios
- [x] Editar usuarios
- [x] Activar/Desactivar usuarios
- [x] Resetear contraseña
- [x] Eliminar usuarios
- [x] Filtrar por rol y estado
- [x] Gestionar permisos por usuario

### **Permisos**
- [x] Crear permisos
- [x] Listar permisos agrupados por módulo
- [x] Editar permisos
- [x] Eliminar permisos
- [x] Asignar permisos a usuarios
- [x] Remover permisos de usuarios
- [x] Verificación dinámica en endpoints
- [x] 30 permisos predefinidos

---

## 🎨 Paleta de Colores (Platónico Theme)

- **Primary**: `#8A1426` (Rojo vino)
- **Secondary**: `#EE8B9A` (Rosa nube)
- **Background**: `#FCE9EC` (Rosa pastel)
- **Text Dark**: `#5E0A15`

---

## 📝 Notas Importantes

1. **Admin Bypass**: Los usuarios con rol `ADMIN` tienen TODOS los permisos automáticamente, sin necesidad de asignación manual.

2. **Seguridad**: Todos los endpoints críticos (crear, editar, eliminar) requieren rol ADMIN.

3. **Permisos Granulares**: Puedes crear permisos personalizados según necesidades del negocio.

4. **UI Responsiva**: Todas las interfaces son mobile-friendly y usan Bootstrap 5.

5. **Validaciones**: Tanto frontend como backend tienen validaciones robustas.

---

## 🔧 Mantenimiento

### **Agregar Nuevo Permiso**

1. Ir a `/admin/permisos`
2. Click en "Nuevo Permiso"
3. Llenar formulario (código, nombre, módulo, descripción)
4. Guardar

### **Agregar Nueva Mesa**

1. Ir a `/admin/mesas`
2. Click en "Nueva Mesa"
3. Llenar datos (número, nombre, capacidad)
4. Guardar

---

## 📚 Documentación API Completa

Acceder a:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## ✨ Características Destacadas

- ✅ Arquitectura limpia con separación de capas
- ✅ Sistema de permisos dinámico y escalable
- ✅ UI moderna con paleta Platónico
- ✅ Validaciones robustas en backend y frontend
- ✅ Documentación automática con OpenAPI
- ✅ Código comentado y mantenible
- ✅ Manejo de errores consistente
- ✅ Respuestas JSON estandarizadas
- ✅ Filtros y búsquedas en tiempo real
- ✅ Estadísticas en dashboards

---

## 👨‍💻 Autor

Desarrollado para el Sistema POS Platónico  
**Versión**: 1.0.0  
**Fecha**: Diciembre 2025

---

## 🆘 Soporte

Para dudas o problemas, revisar:
1. Logs de Uvicorn (errores de backend)
2. Consola del navegador (errores de frontend)
3. `/docs` para verificar endpoints disponibles

