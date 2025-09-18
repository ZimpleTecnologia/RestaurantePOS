#!/usr/bin/env python3
"""
Script simple para revisar la base de datos
"""
import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_db():
    """Revisar la base de datos directamente"""
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
        
        # Verificar restricciones
        print("🔒 Restricciones de la tabla carta_restaurante:")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint 
            WHERE conrelid = 'carta_restaurante'::regclass 
            AND contype = 'c'
        """)
        
        constraints = cur.fetchall()
        for row in constraints:
            print(f"  {row[0]}: {row[1]}")
        
        # Verificar datos existentes
        print("\n📊 Datos existentes:")
        cur.execute("SELECT COUNT(*) FROM carta_restaurante")
        count = cur.fetchone()[0]
        print(f"  Total registros: {count}")
        
        if count > 0:
            cur.execute("SELECT DISTINCT categoria FROM carta_restaurante WHERE categoria IS NOT NULL")
            categories = cur.fetchall()
            print("  Categorías existentes:")
            for cat in categories:
                print(f"    - '{cat[0]}'")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_db()
