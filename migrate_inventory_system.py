#!/usr/bin/env python3
"""
Script de migración para actualizar el sistema de inventario
Agrega los nuevos campos y tipos de productos
"""
import sys
import os
from sqlalchemy import text

# Cargar variables de entorno desde .env si existe
from dotenv import load_dotenv
load_dotenv()

# Si no hay archivo .env, usar configuración por defecto para PostgreSQL local
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://sistema_pos_user:sistema_pos_password@localhost:5432/sistema_pos"
    os.environ["SECRET_KEY"] = "tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion"
    os.environ["ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    os.environ["DEBUG"] = "True"

# Agregar path de la aplicación
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def migrate_database():
    """Ejecutar migración de la base de datos"""
    try:
        from app.database import engine
        
        print("🔄 Iniciando migración del sistema de inventario...")
        
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                # 1. Agregar columna product_type si no existe
                print("📝 Agregando columna product_type...")
                conn.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN IF NOT EXISTS product_type VARCHAR(20) DEFAULT 'sales'
                """))
                
                # Verificar si la columna se creó como ENUM y convertirla a VARCHAR si es necesario
                print("📝 Verificando tipo de columna product_type...")
                result = conn.execute(text("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'products' AND column_name = 'product_type'
                """)).fetchone()
                
                if result and 'enum' in result[0].lower():
                    print("📝 Convirtiendo ENUM a VARCHAR...")
                    conn.execute(text("""
                        ALTER TABLE products 
                        ALTER COLUMN product_type TYPE VARCHAR(20) 
                        USING product_type::text
                    """))
                
                # 2. Agregar columna purchase_price si no existe
                print("📝 Agregando columna purchase_price...")
                conn.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN IF NOT EXISTS purchase_price NUMERIC(10,2)
                """))
                
                # 3. Actualizar track_stock por defecto a True
                print("📝 Actualizando track_stock por defecto...")
                conn.execute(text("""
                    ALTER TABLE products 
                    ALTER COLUMN track_stock SET DEFAULT true
                """))
                
                # 4. Agregar columna total_cost a recipes si no existe
                print("📝 Agregando columna total_cost a recipes...")
                conn.execute(text("""
                    ALTER TABLE recipes 
                    ADD COLUMN IF NOT EXISTS total_cost NUMERIC(10,2)
                """))
                
                # 5. Agregar columnas de costo a recipe_items si no existen
                print("📝 Agregando columnas de costo a recipe_items...")
                conn.execute(text("""
                    ALTER TABLE recipe_items 
                    ADD COLUMN IF NOT EXISTS unit_cost NUMERIC(10,2)
                """))
                conn.execute(text("""
                    ALTER TABLE recipe_items 
                    ADD COLUMN IF NOT EXISTS total_cost NUMERIC(10,2)
                """))
                
                # 6. Crear índices para optimización
                print("📝 Creando índices de optimización...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_products_product_type 
                    ON products(product_type)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_products_supplier_id 
                    ON products(supplier_id)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_recipe_items_product_id 
                    ON recipe_items(product_id)
                """))
                
                # 7. Actualizar productos existentes
                print("📝 Actualizando productos existentes...")
                
                # Primero, establecer todos los productos existentes como 'sales' por defecto
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
                
                # 8. Crear categorías por defecto si no existen
                print("📝 Creando categorías por defecto...")
                conn.execute(text("""
                    INSERT INTO categories (name, description, is_active) 
                    VALUES 
                        ('Materias Primas', 'Ingredientes y materias primas para preparación', true),
                        ('Platos Principales', 'Platos principales del menú', true),
                        ('Bebidas', 'Bebidas y refrescos', true),
                        ('Postres', 'Postres y dulces', true)
                    ON CONFLICT (name) DO NOTHING
                """))
                
                # 9. Crear ubicación por defecto si no existe
                print("📝 Creando ubicación por defecto...")
                conn.execute(text("""
                    INSERT INTO inventory_locations (name, description, is_active, is_default) 
                    VALUES ('Almacén Principal', 'Ubicación principal del almacén', true, true)
                    ON CONFLICT (name) DO NOTHING
                """))
                
                # Confirmar transacción
                trans.commit()
                print("✅ Migración completada exitosamente")
                
                # Mostrar estadísticas
                result = conn.execute(text("""
                    SELECT 
                        product_type,
                        COUNT(*) as count
                    FROM products 
                    WHERE is_active = true
                    GROUP BY product_type
                """))
                
                print("\n📊 Estadísticas de productos:")
                for row in result:
                    print(f"   {row.product_type}: {row.count} productos")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error durante la migración: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False

def create_sample_data():
    """Crear datos de ejemplo para el nuevo sistema"""
    try:
        from app.database import SessionLocal
        from app.models.product import Product, ProductType, Category
        from app.models.recipe import Recipe, RecipeItem
        
        print("\n🌱 Creando datos de ejemplo...")
        
        db = SessionLocal()
        
        try:
            # Obtener categorías
            materias_primas = db.query(Category).filter(Category.name == "Materias Primas").first()
            platos_principales = db.query(Category).filter(Category.name == "Platos Principales").first()
            
            if not materias_primas or not platos_principales:
                print("⚠️ Categorías no encontradas, saltando creación de datos de ejemplo")
                return True
            
            # Crear productos de inventario (materias primas)
            inventory_products = [
                {
                    "name": "Arroz 10KG",
                    "code": "ARR001",
                    "product_type": ProductType.INVENTORY,
                    "category_id": materias_primas.id,
                    "stock_quantity": 50,
                    "min_stock_level": 10,
                    "purchase_price": 25.00,
                    "unit": "kg",
                    "price": 0  # No se vende directamente
                },
                {
                    "name": "Pollo 40 porciones",
                    "code": "POL001",
                    "product_type": ProductType.INVENTORY,
                    "category_id": materias_primas.id,
                    "stock_quantity": 30,
                    "min_stock_level": 5,
                    "purchase_price": 45.00,
                    "unit": "porciones",
                    "price": 0
                },
                {
                    "name": "Carne 50 porciones",
                    "code": "CAR001",
                    "product_type": ProductType.INVENTORY,
                    "category_id": materias_primas.id,
                    "stock_quantity": 25,
                    "min_stock_level": 8,
                    "purchase_price": 60.00,
                    "unit": "porciones",
                    "price": 0
                },
                {
                    "name": "Costilla Cerdo 2KG",
                    "code": "COS001",
                    "product_type": ProductType.INVENTORY,
                    "category_id": materias_primas.id,
                    "stock_quantity": 15,
                    "min_stock_level": 3,
                    "purchase_price": 35.00,
                    "unit": "kg",
                    "price": 0
                }
            ]
            
            created_inventory = []
            for product_data in inventory_products:
                existing = db.query(Product).filter(Product.code == product_data["code"]).first()
                if not existing:
                    product = Product(**product_data)
                    db.add(product)
                    created_inventory.append(product)
            
            # Crear productos de venta (platos)
            sales_products = [
                {
                    "name": "Costilla en Salsa BBQ",
                    "code": "PLA001",
                    "product_type": ProductType.SALES,
                    "category_id": platos_principales.id,
                    "stock_quantity": 0,  # No se maneja stock para platos
                    "min_stock_level": 0,
                    "price": 25.00,
                    "unit": "plato"
                },
                {
                    "name": "Pollo a la Plancha",
                    "code": "PLA002",
                    "product_type": ProductType.SALES,
                    "category_id": platos_principales.id,
                    "stock_quantity": 0,
                    "min_stock_level": 0,
                    "price": 18.00,
                    "unit": "plato"
                }
            ]
            
            created_sales = []
            for product_data in sales_products:
                existing = db.query(Product).filter(Product.code == product_data["code"]).first()
                if not existing:
                    product = Product(**product_data)
                    db.add(product)
                    created_sales.append(product)
            
            db.commit()
            
            # Crear recetas para los productos de venta
            if created_sales and created_inventory:
                # Receta para Costilla en Salsa BBQ
                costilla_bbq = next((p for p in created_sales if p.code == "PLA001"), None)
                costilla_ingredient = next((p for p in created_inventory if p.code == "COS001"), None)
                
                if costilla_bbq and costilla_ingredient:
                    recipe = Recipe(
                        name="Receta Costilla BBQ",
                        description="Receta para preparar costilla en salsa BBQ",
                        product_id=costilla_bbq.id,
                        preparation_time=45
                    )
                    db.add(recipe)
                    db.flush()
                    
                    # Agregar ingrediente a la receta
                    recipe_item = RecipeItem(
                        recipe_id=recipe.id,
                        product_id=costilla_ingredient.id,
                        quantity=0.5,  # 0.5 kg de costilla por plato
                        unit="kg"
                    )
                    db.add(recipe_item)
                
                # Receta para Pollo a la Plancha
                pollo_plancha = next((p for p in created_sales if p.code == "PLA002"), None)
                pollo_ingredient = next((p for p in created_inventory if p.code == "POL001"), None)
                
                if pollo_plancha and pollo_ingredient:
                    recipe = Recipe(
                        name="Receta Pollo Plancha",
                        description="Receta para preparar pollo a la plancha",
                        product_id=pollo_plancha.id,
                        preparation_time=30
                    )
                    db.add(recipe)
                    db.flush()
                    
                    # Agregar ingrediente a la receta
                    recipe_item = RecipeItem(
                        recipe_id=recipe.id,
                        product_id=pollo_ingredient.id,
                        quantity=1,  # 1 porción de pollo por plato
                        unit="porción"
                    )
                    db.add(recipe_item)
            
            db.commit()
            print("✅ Datos de ejemplo creados exitosamente")
            
            print(f"   📦 Productos de inventario creados: {len(created_inventory)}")
            print(f"   🍽️ Productos de venta creados: {len(created_sales)}")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creando datos de ejemplo: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando migración del sistema de inventario...")
    
    # Ejecutar migración
    if not migrate_database():
        print("❌ Migración falló")
        return False
    
    # Crear datos de ejemplo
    if not create_sample_data():
        print("⚠️ Error creando datos de ejemplo, pero la migración fue exitosa")
    
    print("\n🎉 Migración completada exitosamente!")
    print("\n📋 Resumen de cambios:")
    print("   ✅ Agregado campo product_type a productos")
    print("   ✅ Agregado campo purchase_price para materias primas")
    print("   ✅ Mejorado sistema de recetas con costos")
    print("   ✅ Creados índices de optimización")
    print("   ✅ Creadas categorías y ubicaciones por defecto")
    print("   ✅ Creados productos y recetas de ejemplo")
    
    print("\n🔧 Próximos pasos:")
    print("   1. Reiniciar la aplicación")
    print("   2. Verificar que los nuevos endpoints funcionan")
    print("   3. Configurar recetas para productos existentes")
    print("   4. Probar el consumo automático de inventario")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
