#!/usr/bin/env python3
"""
Script agresivo para eliminar completamente el ENUM producttype
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

def fix_enum_aggressive():
    """Eliminar completamente el ENUM y recrear como VARCHAR"""
    try:
        # Crear conexión directa a la base de datos
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        
        print("🔄 Conectando a la base de datos...")
        
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                # 1. Verificar si existe el ENUM producttype
                print("📝 Verificando ENUM producttype...")
                result = conn.execute(text("""
                    SELECT typname 
                    FROM pg_type 
                    WHERE typname = 'producttype'
                """)).fetchone()
                
                if result:
                    print(f"   ENUM encontrado: {result[0]}")
                    
                    # 2. Eliminar la columna que usa el ENUM
                    print("📝 Eliminando columna product_type...")
                    conn.execute(text("""
                        ALTER TABLE products DROP COLUMN IF EXISTS product_type
                    """))
                    
                    # 3. Eliminar el ENUM type
                    print("📝 Eliminando ENUM producttype...")
                    conn.execute(text("""
                        DROP TYPE IF EXISTS producttype
                    """))
                    
                    # 4. Recrear la columna como VARCHAR
                    print("📝 Recreando columna product_type como VARCHAR...")
                    conn.execute(text("""
                        ALTER TABLE products 
                        ADD COLUMN product_type VARCHAR(20) DEFAULT 'sales'
                    """))
                    
                    print("✅ ENUM eliminado y columna recreada como VARCHAR")
                else:
                    print("✅ No se encontró ENUM producttype")
                
                # 5. Verificar y agregar purchase_price si no existe
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
                
                # 6. Actualizar productos existentes
                print("📝 Actualizando productos existentes...")
                
                # Establecer todos los productos como 'sales' por defecto
                conn.execute(text("""
                    UPDATE products 
                    SET product_type = 'sales' 
                    WHERE product_type IS NULL
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
                
                # 7. Crear índices si no existen
                print("📝 Creando índices...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_products_product_type 
                    ON products(product_type)
                """))
                
                # 8. Verificar el resultado
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
                
                # Verificar el tipo de la columna
                result = conn.execute(text("""
                    SELECT column_name, data_type, udt_name
                    FROM information_schema.columns 
                    WHERE table_name = 'products' AND column_name = 'product_type'
                """)).fetchone()
                
                if result:
                    print(f"✅ Tipo de columna: {result[1]} (UDT: {result[2]})")
                
                # Confirmar transacción
                trans.commit()
                print("✅ Corrección completada exitosamente")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error durante la corrección: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando corrección agresiva del ENUM...")
    
    if fix_enum_aggressive():
        print("\n🎉 ¡Corrección completada exitosamente!")
        print("\n📋 Resumen de cambios:")
        print("   ✅ ENUM producttype eliminado completamente")
        print("   ✅ Columna product_type recreada como VARCHAR")
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
