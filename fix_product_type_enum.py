#!/usr/bin/env python3
"""
Script para corregir el problema del ENUM en product_type
"""
import sys
import os
from sqlalchemy import text, create_engine

# Cargar variables de entorno desde .env si existe
from dotenv import load_dotenv
load_dotenv()

# Si no hay archivo .env, usar configuración por defecto
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://sistema_pos_user:sistema_pos_password@localhost:5432/sistema_pos"

def fix_product_type_enum():
    """Corregir el problema del ENUM en product_type"""
    try:
        # Crear conexión directa a la base de datos
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        
        print("🔄 Conectando a la base de datos...")
        
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                # 1. Verificar si la columna product_type existe y su tipo
                print("📝 Verificando columna product_type...")
                result = conn.execute(text("""
                    SELECT column_name, data_type, udt_name
                    FROM information_schema.columns 
                    WHERE table_name = 'products' AND column_name = 'product_type'
                """)).fetchone()
                
                if result:
                    print(f"   Columna encontrada: {result[0]}, Tipo: {result[1]}, UDT: {result[2]}")
                    
                    # Si es un ENUM, necesitamos eliminarlo y recrearlo como VARCHAR
                    if 'enum' in result[2].lower():
                        print("📝 Detectado ENUM, convirtiendo a VARCHAR...")
                        
                        # Eliminar la columna ENUM
                        conn.execute(text("""
                            ALTER TABLE products DROP COLUMN IF EXISTS product_type
                        """))
                        
                        # Recrear como VARCHAR
                        conn.execute(text("""
                            ALTER TABLE products 
                            ADD COLUMN product_type VARCHAR(20) DEFAULT 'sales'
                        """))
                        
                        print("✅ Columna product_type recreada como VARCHAR")
                    else:
                        print("✅ Columna product_type ya es VARCHAR")
                else:
                    print("📝 Columna product_type no existe, creándola...")
                    conn.execute(text("""
                        ALTER TABLE products 
                        ADD COLUMN product_type VARCHAR(20) DEFAULT 'sales'
                    """))
                
                # 2. Verificar y agregar purchase_price si no existe
                print("📝 Verificando columna purchase_price...")
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'products' AND column_name = 'purchase_price'
                """)).fetchone()
                
                if not result:
                    print("📝 Agregando columna purchase_price...")
                    conn.execute(text("""
                        ALTER TABLE products 
                        ADD COLUMN purchase_price NUMERIC(10,2)
                    """))
                else:
                    print("✅ Columna purchase_price ya existe")
                
                # 3. Actualizar productos existentes
                print("📝 Actualizando productos existentes...")
                
                # Establecer todos los productos como 'sales' por defecto
                conn.execute(text("""
                    UPDATE products 
                    SET product_type = 'sales' 
                    WHERE product_type IS NULL OR product_type = ''
                """))
                
                # Marcar productos con stock > 0 como productos de inventario
                conn.execute(text("""
                    UPDATE products 
                    SET product_type = 'inventory' 
                    WHERE stock_quantity > 0 AND product_type = 'sales'
                """))
                
                # Marcar productos con precio de costo como productos de inventario
                conn.execute(text("""
                    UPDATE products 
                    SET product_type = 'inventory' 
                    WHERE cost_price > 0 AND product_type = 'sales'
                """))
                
                # 4. Crear índices si no existen
                print("📝 Creando índices...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_products_product_type 
                    ON products(product_type)
                """))
                
                # 5. Verificar el resultado
                print("📝 Verificando resultado...")
                result = conn.execute(text("""
                    SELECT product_type, COUNT(*) as count
                    FROM products 
                    WHERE is_active = true
                    GROUP BY product_type
                """)).fetchall()
                
                print("📊 Productos por tipo:")
                for row in result:
                    print(f"   {row[0]}: {row[1]} productos")
                
                # Confirmar transacción
                trans.commit()
                print("✅ Migración completada exitosamente")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error durante la migración: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando corrección del ENUM product_type...")
    
    if fix_product_type_enum():
        print("\n🎉 ¡Corrección completada exitosamente!")
        print("\n📋 Resumen de cambios:")
        print("   ✅ Columna product_type convertida a VARCHAR")
        print("   ✅ Columna purchase_price agregada")
        print("   ✅ Productos existentes actualizados")
        print("   ✅ Índices creados")
        
        print("\n🔧 Próximos pasos:")
        print("   1. Ejecutar el script de migración principal")
        print("   2. Verificar que la aplicación funciona correctamente")
        
        return True
    else:
        print("❌ Corrección falló")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
