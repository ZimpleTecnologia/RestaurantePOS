#!/bin/bash

# Script para exportar la estructura de la base de datos con datos de ejemplo
# Uso: ./export_with_sample_data.sh

echo "Exportando estructura y datos de ejemplo de la base de datos..."

# Exportar estructura y datos
docker exec sistema_pos_db pg_dump \
    -h localhost \
    -U sistema_pos_user \
    -d sistema_pos \
    --no-owner \
    --no-privileges \
    > db_structure_with_sample_data.sql

echo "Estructura y datos exportados a: db_structure_with_sample_data.sql"
