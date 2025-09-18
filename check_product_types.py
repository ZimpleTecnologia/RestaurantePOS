#!/usr/bin/env python3
"""
Script para verificar y actualizar los tipos de productos en la base de datos
"""

def check_and_update_product_types():
    """Verificar y actualizar tipos de productos"""
    try:
        print("🔄 Verificando tipos de productos...")
        
        # Importar dependencias
        from app.database import SessionLocal
        from app.models.product import Product, ProductType
        from sqlalchemy import text
        
        db = SessionLocal()
        
        try:
            # Verificar productos sin tipo
            print("\n🔄 Verificando productos sin tipo...")
            productos_sin_tipo = db.query(Product).filter(Product.product_type.is_(None)).all()
            print(f"✅ Productos sin tipo: {len(productos_sin_tipo)}")
            
            if productos_sin_tipo:
                print("📋 Productos sin tipo:")
                for product in productos_sin_tipo:
                    print(f"  - ID: {product.id}, Nombre: {product.name}, Categoría: {product.category}")
            
            # Verificar productos con tipo
            print("\n🔄 Verificando productos con tipo...")
            productos_con_tipo = db.query(Product).filter(Product.product_type.isnot(None)).all()
            print(f"✅ Productos con tipo: {len(productos_con_tipo)}")
            
            # Contar por tipo
            sales_count = db.query(Product).filter(Product.product_type == ProductType.SALES).count()
            inventory_count = db.query(Product).filter(Product.product_type == ProductType.INVENTORY).count()
            
            print(f"  - Productos de venta (SALES): {sales_count}")
            print(f"  - Productos de inventario (INVENTORY): {inventory_count}")
            
            # Sugerir actualizaciones basadas en categorías
            print("\n🔄 Analizando categorías para sugerir tipos...")
            
            # Productos que probablemente son de inventario
            categorias_inventario = ['INGREDIENTE', 'UTENSILIO']
            for categoria in categorias_inventario:
                productos_categoria = db.query(Product).filter(Product.category == categoria).all()
                print(f"  - Categoría {categoria}: {len(productos_categoria)} productos")
            
            # Productos que probablemente son de venta
            categorias_venta = ['ENTRADA', 'PLATO_PRINCIPAL', 'POSTRE', 'BEBIDA', 'ALCOHOL']
            for categoria in categorias_venta:
                productos_categoria = db.query(Product).filter(Product.category == categoria).all()
                print(f"  - Categoría {categoria}: {len(productos_categoria)} productos")
            
            # Mostrar algunos ejemplos
            print("\n📋 Ejemplos de productos por categoría:")
            for categoria in categorias_venta + categorias_inventario:
                productos = db.query(Product).filter(Product.category == categoria).limit(3).all()
                if productos:
                    print(f"  {categoria}:")
                    for product in productos:
                        print(f"    - {product.name} (Tipo: {product.product_type})")
            
            print("\n🎉 Verificación completada!")
            
        except Exception as e:
            print(f"❌ Error en verificación: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_and_update_product_types()
