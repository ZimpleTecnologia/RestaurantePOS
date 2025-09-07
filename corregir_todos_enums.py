#!/usr/bin/env python3
"""
Script para corregir todos los valores de ENUMs en la base de datos
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def corregir_todos_enums():
    """Corregir todos los valores de ENUMs"""
    try:
        # Configurar conexión a la base de datos
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/restaurante_pos")
        engine = create_engine(database_url)
        
        print("🔧 Corrigiendo todos los valores de ENUMs...")
        print("=" * 60)
        
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                # 1. Corregir ProductType
                print("📋 1. Corrigiendo ProductType...")
                result = conn.execute(text("""
                    SELECT DISTINCT product_type, COUNT(*) as cantidad
                    FROM products 
                    WHERE product_type IS NOT NULL
                    GROUP BY product_type
                    ORDER BY product_type
                """)).fetchall()
                
                print("   Valores actuales:")
                for row in result:
                    print(f"     - '{row[0]}': {row[1]} productos")
                
                # Actualizar a mayúsculas
                result = conn.execute(text("""
                    UPDATE products 
                    SET product_type = 'INVENTORY' 
                    WHERE product_type = 'inventory'
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos de 'inventory' a 'INVENTORY'")
                
                result = conn.execute(text("""
                    UPDATE products 
                    SET product_type = 'SALES' 
                    WHERE product_type = 'sales'
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos de 'sales' a 'SALES'")
                
                # 2. Corregir ProductCategory
                print("\n📋 2. Corrigiendo ProductCategory...")
                result = conn.execute(text("""
                    SELECT DISTINCT category, COUNT(*) as cantidad
                    FROM products 
                    WHERE category IS NOT NULL
                    GROUP BY category
                    ORDER BY category
                """)).fetchall()
                
                print("   Valores actuales:")
                for row in result:
                    print(f"     - '{row[0]}': {row[1]} productos")
                
                # Mapeo de valores a corregir
                category_mapping = {
                    'otro': 'OTRO',
                    'entrada': 'ENTRADA',
                    'plato_principal': 'PLATO_PRINCIPAL',
                    'postre': 'POSTRE',
                    'bebida': 'BEBIDA',
                    'ensalada': 'ENSALADA',
                    'sopa': 'SOPA',
                    'sandwich': 'SANDWICH',
                    'pizza': 'PIZZA',
                    'pasta': 'PASTA',
                    'carne': 'CARNE',
                    'pollo': 'POLLO',
                    'pescado': 'PESCADO',
                    'vegetariano': 'VEGETARIANO',
                    'vegano': 'VEGANO'
                }
                
                for old_value, new_value in category_mapping.items():
                    result = conn.execute(text("""
                        UPDATE products 
                        SET category = :new_value 
                        WHERE category = :old_value
                    """), {"old_value": old_value, "new_value": new_value})
                    if result.rowcount > 0:
                        print(f"   ✅ Actualizados {result.rowcount} productos de '{old_value}' a '{new_value}'")
                
                # 3. Verificar valores después de las correcciones
                print("\n📋 3. Verificación final...")
                
                # ProductType
                result = conn.execute(text("""
                    SELECT DISTINCT product_type, COUNT(*) as cantidad
                    FROM products 
                    WHERE product_type IS NOT NULL
                    GROUP BY product_type
                    ORDER BY product_type
                """)).fetchall()
                
                print("   ProductType después de la corrección:")
                for row in result:
                    print(f"     - '{row[0]}': {row[1]} productos")
                
                # ProductCategory
                result = conn.execute(text("""
                    SELECT DISTINCT category, COUNT(*) as cantidad
                    FROM products 
                    WHERE category IS NOT NULL
                    GROUP BY category
                    ORDER BY category
                """)).fetchall()
                
                print("   ProductCategory después de la corrección:")
                for row in result:
                    print(f"     - '{row[0]}': {row[1]} productos")
                
                # 4. Verificar que no queden valores en minúsculas
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM products 
                    WHERE product_type IN ('inventory', 'sales')
                       OR category IN ('otro', 'entrada', 'plato_principal', 'postre', 'bebida', 
                                      'ensalada', 'sopa', 'sandwich', 'pizza', 'pasta', 
                                      'carne', 'pollo', 'pescado', 'vegetariano', 'vegano')
                """)).fetchone()
                
                if result[0] == 0:
                    print("\n✅ Todos los valores están en mayúsculas")
                else:
                    print(f"\n⚠️  Aún quedan {result[0]} productos con valores en minúsculas")
                
                # Confirmar transacción
                trans.commit()
                print("\n✅ Corrección de ENUMs completada exitosamente")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error durante la corrección: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    corregir_todos_enums()
