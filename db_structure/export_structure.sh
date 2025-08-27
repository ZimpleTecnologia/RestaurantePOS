#!/bin/bash

# Script para exportar solo la estructura de la base de datos
# Uso: ./export_structure.sh

echo "Exportando estructura de la base de datos..."

# Exportar solo la estructura (sin datos)
docker exec sistema_pos_db pg_dump \
    -h localhost \
    -U sistema_pos_user \
    -d sistema_pos \
    --schema-only \
    --no-owner \
    --no-privileges \
    > db_structure_only.sql

echo "Estructura exportada a: db_structure_only.sql"
