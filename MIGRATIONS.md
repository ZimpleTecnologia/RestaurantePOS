# Migraciones de Base de Datos

Este proyecto usa **Alembic** para el control de versiones de la base de datos.

## Estructura

```
alembic/
├── env.py              # Configuración del entorno de migraciones
├── script.py.mako      # Plantilla para nuevas migraciones
├── versions/           # Directorio con archivos de migración
└── __init__.py
```

## Configuración

La URL de la base de datos se configura mediante la variable de entorno:

```bash
export DATABASE_URL="postgresql://usuario:password@host:5432/db_name"
```

O se puede configurar en el archivo `.env`:

```env
DATABASE_URL=postgresql://sistema_pos_user:password@localhost:5432/sistema_pos
```

## Uso del Script de Migraciones

El proyecto incluye un script helper en `scripts/migration.py`:

### Inicializar Base de Datos (sin migraciones)
```bash
python scripts/migration.py init
```
Crea todas las tablas usando SQLAlchemy. Útil para desarrollo inicial.

### Generar Nueva Migración
```bash
python scripts/migration.py generate "descripción de cambios"
```
Genera automáticamente una migración basada en los cambios de los modelos.

### Aplicar Migraciones
```bash
python scripts/migration.py migrate
```
Aplica todas las migraciones pendientes.

### Revertir Última Migración
```bash
python scripts/migration.py rollback
```
Revierte la última migración aplicada.

### Ver Historial
```bash
python scripts/migration.py history
```
Muestra todas las migraciones aplicadas.

### Ver Migración Actual
```bash
python scripts/migration.py current
```
Muestra qué migración está actualmente aplicada.

## Uso Directo de Alembic

También puedes usar Alembic directamente:

```bash
# Generar migración automática
alembic revision --autogenerate -m "tu mensaje"

# Aplicar migraciones
alembic upgrade head

# Revertir una migración
alembic downgrade -1

# Ver historial
alembic history
```

## Notas Importantes

1. **Antes de generar una migración**: Asegúrate de que los modelos estén correctamente definidos en `app/models/`

2. **Revisa las migraciones generadas**: Alembic puede no detectar todos los cambios correctamente. Revisa el código generado.

3. **Backups**: Siempre haz backup de la base de datos antes de aplicar migraciones en producción.

4. **Entorno de desarrollo**: Para desarrollo local, puedes usar `python scripts/migration.py init` para crear las tablas rápidamente.
