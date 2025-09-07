#!/usr/bin/env python3
"""
Script para corregir los valores del ENUM ProductType en la base de datos
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def corregir_enum_productos():
    """Corregir los valores del ENUM ProductType"""
    try:
        # Configurar conexión a la base de datos
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/restaurante_pos")
        engine = create_engine(database_url)
        
        print("🔧 Corrigiendo valores del ENUM ProductType...")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                # 1. Verificar valores actuales
                print("📋 Valores actuales en la base de datos:")
                result = conn.execute(text("""
                    SELECT DISTINCT product_type, COUNT(*) as cantidad
                    FROM products 
                    WHERE product_type IS NOT NULL
                    GROUP BY product_type
                    ORDER BY product_type
                """)).fetchall()
                
                for row in result:
                    print(f"   - '{row[0]}': {row[1]} productos")
                
                # 2. Actualizar valores a mayúsculas
                print("\n🔄 Actualizando valores a mayúsculas...")
                
                # Actualizar 'inventory' a 'INVENTORY'
                result = conn.execute(text("""
                    UPDATE products 
                    SET product_type = 'INVENTORY' 
                    WHERE product_type = 'inventory'
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos de 'inventory' a 'INVENTORY'")
                
                # Actualizar 'sales' a 'SALES'
                result = conn.execute(text("""
                    UPDATE products 
                    SET product_type = 'SALES' 
                    WHERE product_type = 'sales'
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos de 'sales' a 'SALES'")
                
                # 3. Verificar valores después de la actualización
                print("\n📋 Valores después de la corrección:")
                result = conn.execute(text("""
                    SELECT DISTINCT product_type, COUNT(*) as cantidad
                    FROM products 
                    WHERE product_type IS NOT NULL
                    GROUP BY product_type
                    ORDER BY product_type
                """)).fetchall()
                
                for row in result:
                    print(f"   - '{row[0]}': {row[1]} productos")
                
                # 4. Verificar que no queden valores en minúsculas
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM products 
                    WHERE product_type IN ('inventory', 'sales')
                """)).fetchone()
                
                if result[0] == 0:
                    print("\n✅ Todos los valores están en mayúsculas")
                else:
                    print(f"\n⚠️  Aún quedan {result[0]} productos con valores en minúsculas")
                
                # Confirmar transacción
                trans.commit()
                print("\n✅ Corrección completada exitosamente")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error durante la corrección: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    corregir_enum_productos()
