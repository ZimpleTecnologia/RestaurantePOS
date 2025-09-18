#!/usr/bin/env python3
"""
Script para verificar las tablas de menús en la base de datos
"""
import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_menu_tables():
    """Verificar las tablas de menús"""
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'restaurante_pos'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
        
        cur = conn.cursor()
        
        # Verificar tablas relacionadas con menús
        print("🔍 Verificando tablas de menús...")
        
        # Listar todas las tablas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%menu%'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"\n📋 Tablas relacionadas con menús:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Verificar estructura de cada tabla
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 Estructura de {table_name}:")
            
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            for col in columns:
                print(f"    {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            
            # Verificar claves foráneas
            cur.execute(f"""
                SELECT 
                    tc.constraint_name, 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name='{table_name}'
            """)
            
            fks = cur.fetchall()
            if fks:
                print(f"    Claves foráneas:")
                for fk in fks:
                    print(f"      {fk[2]} -> {fk[3]}.{fk[4]}")
        
        # Verificar datos existentes
        print(f"\n📊 Datos existentes:")
        for table in tables:
            table_name = table[0]
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"  {table_name}: {count} registros")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_menu_tables()
