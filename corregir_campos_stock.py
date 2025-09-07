#!/usr/bin/env python3
"""
Script para corregir los campos de stock que están en NULL
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def corregir_campos_stock():
    """Corregir campos de stock que están en NULL"""
    try:
        # Configurar conexión a la base de datos
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/restaurante_pos")
        engine = create_engine(database_url)
        
        print("🔧 Corrigiendo campos de stock NULL...")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                # 1. Verificar productos con campos NULL
                print("📋 Verificando productos con campos NULL...")
                result = conn.execute(text("""
                    SELECT id, name, stock_quantity, min_stock_level, max_stock_level, stock, min_stock, max_stock
                    FROM products 
                    WHERE stock_quantity IS NULL 
                       OR min_stock_level IS NULL 
                       OR max_stock_level IS NULL
                       OR stock IS NULL 
                       OR min_stock IS NULL 
                       OR max_stock IS NULL
                    ORDER BY id
                """)).fetchall()
                
                print(f"   Encontrados {len(result)} productos con campos NULL:")
                for row in result:
                    print(f"     ID {row[0]}: {row[1]}")
                    print(f"       stock_quantity: {row[2]}, min_stock_level: {row[3]}, max_stock_level: {row[4]}")
                    print(f"       stock: {row[5]}, min_stock: {row[6]}, max_stock: {row[7]}")
                
                # 2. Actualizar campos NULL con valores por defecto
                print("\n🔄 Actualizando campos NULL con valores por defecto...")
                
                # Actualizar stock_quantity
                result = conn.execute(text("""
                    UPDATE products 
                    SET stock_quantity = 0 
                    WHERE stock_quantity IS NULL
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos: stock_quantity = 0")
                
                # Actualizar min_stock_level
                result = conn.execute(text("""
                    UPDATE products 
                    SET min_stock_level = 0 
                    WHERE min_stock_level IS NULL
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos: min_stock_level = 0")
                
                # Actualizar max_stock_level
                result = conn.execute(text("""
                    UPDATE products 
                    SET max_stock_level = 100 
                    WHERE max_stock_level IS NULL
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos: max_stock_level = 100")
                
                # Actualizar stock (alias)
                result = conn.execute(text("""
                    UPDATE products 
                    SET stock = 0 
                    WHERE stock IS NULL
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos: stock = 0")
                
                # Actualizar min_stock (alias)
                result = conn.execute(text("""
                    UPDATE products 
                    SET min_stock = 0 
                    WHERE min_stock IS NULL
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos: min_stock = 0")
                
                # Actualizar max_stock (alias)
                result = conn.execute(text("""
                    UPDATE products 
                    SET max_stock = 100 
                    WHERE max_stock IS NULL
                """))
                print(f"   ✅ Actualizados {result.rowcount} productos: max_stock = 100")
                
                # 3. Sincronizar campos de stock
                print("\n🔄 Sincronizando campos de stock...")
                
                # Sincronizar stock con stock_quantity
                result = conn.execute(text("""
                    UPDATE products 
                    SET stock = stock_quantity 
                    WHERE stock != stock_quantity OR stock IS NULL
                """))
                print(f"   ✅ Sincronizados {result.rowcount} productos: stock = stock_quantity")
                
                # Sincronizar min_stock con min_stock_level
                result = conn.execute(text("""
                    UPDATE products 
                    SET min_stock = min_stock_level 
                    WHERE min_stock != min_stock_level OR min_stock IS NULL
                """))
                print(f"   ✅ Sincronizados {result.rowcount} productos: min_stock = min_stock_level")
                
                # Sincronizar max_stock con max_stock_level
                result = conn.execute(text("""
                    UPDATE products 
                    SET max_stock = max_stock_level 
                    WHERE max_stock != max_stock_level OR max_stock IS NULL
                """))
                print(f"   ✅ Sincronizados {result.rowcount} productos: max_stock = max_stock_level")
                
                # 4. Verificar que no queden campos NULL
                print("\n📋 Verificación final...")
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM products 
                    WHERE stock_quantity IS NULL 
                       OR min_stock_level IS NULL 
                       OR max_stock_level IS NULL
                       OR stock IS NULL 
                       OR min_stock IS NULL 
                       OR max_stock IS NULL
                """)).fetchone()
                
                if result[0] == 0:
                    print("   ✅ Todos los campos de stock tienen valores")
                else:
                    print(f"   ⚠️  Aún quedan {result[0]} productos con campos NULL")
                
                # 5. Mostrar resumen de productos
                result = conn.execute(text("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN product_type = 'INVENTORY' THEN 1 ELSE 0 END) as inventario,
                           SUM(CASE WHEN product_type = 'SALES' THEN 1 ELSE 0 END) as ventas
                    FROM products 
                    WHERE is_active = true
                """)).fetchone()
                
                print(f"\n📊 Resumen de productos:")
                print(f"   Total activos: {result[0]}")
                print(f"   Inventario: {result[1]}")
                print(f"   Ventas: {result[2]}")
                
                # Confirmar transacción
                trans.commit()
                print("\n✅ Corrección de campos de stock completada exitosamente")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error durante la corrección: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    corregir_campos_stock()
