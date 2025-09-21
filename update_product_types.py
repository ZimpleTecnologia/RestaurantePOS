#!/usr/bin/env python3
"""
Script para actualizar automáticamente los tipos de productos basándose en sus categorías
"""

def update_product_types():
    """Actualizar tipos de productos basándose en categorías"""
    try:
        print("🔄 Actualizando tipos de productos...")
        
        # Importar dependencias
        from app.database import SessionLocal
        from app.models.product import Product, ProductType, ProductCategory
        
        db = SessionLocal()
        
        try:
            # Definir categorías por tipo
            categorias_venta = [
                ProductCategory.ENTRADA,
                ProductCategory.PLATO_PRINCIPAL,
                ProductCategory.POSTRE,
                ProductCategory.BEBIDA,
                ProductCategory.ALCOHOL
            ]
            
            categorias_inventario = [
                ProductCategory.INGREDIENTE,
                ProductCategory.UTENSILIO
            ]
            
            # Actualizar productos de venta
            print("\n🔄 Actualizando productos de venta...")
            productos_venta = db.query(Product).filter(
                Product.category.in_(categorias_venta),
                Product.product_type != ProductType.SALES
            ).all()
            
            print(f"📋 Productos a actualizar como SALES: {len(productos_venta)}")
            for product in productos_venta:
                print(f"  - {product.name} (Categoría: {product.category})")
                product.product_type = ProductType.SALES
            
            # Actualizar productos de inventario
            print("\n🔄 Actualizando productos de inventario...")
            productos_inventario = db.query(Product).filter(
                Product.category.in_(categorias_inventario),
                Product.product_type != ProductType.INVENTORY
            ).all()
            
            print(f"📋 Productos a actualizar como INVENTORY: {len(productos_inventario)}")
            for product in productos_inventario:
                print(f"  - {product.name} (Categoría: {product.category})")
                product.product_type = ProductType.INVENTORY
            
            # Actualizar productos con categoría OTRO
            print("\n🔄 Actualizando productos con categoría OTRO...")
            productos_otro = db.query(Product).filter(
                Product.category == ProductCategory.OTRO,
                Product.product_type.is_(None)
            ).all()
            
            print(f"📋 Productos con categoría OTRO: {len(productos_otro)}")
            for product in productos_otro:
                print(f"  - {product.name} (Categoría: {product.category})")
                # Por defecto, categoría OTRO se considera de venta
                product.product_type = ProductType.SALES
            
            # Confirmar cambios
            if productos_venta or productos_inventario or productos_otro:
                confirm = input("\n¿Desea aplicar estos cambios? (s/n): ")
                if confirm.lower() == 's':
                    db.commit()
                    print("✅ Cambios aplicados exitosamente!")
                else:
                    db.rollback()
                    print("❌ Cambios cancelados")
            else:
                print("ℹ️ No hay productos que actualizar")
            
            # Verificar resultado
            print("\n🔄 Verificando resultado...")
            sales_count = db.query(Product).filter(Product.product_type == ProductType.SALES).count()
            inventory_count = db.query(Product).filter(Product.product_type == ProductType.INVENTORY).count()
            sin_tipo_count = db.query(Product).filter(Product.product_type.is_(None)).count()
            
            print(f"✅ Productos de venta (SALES): {sales_count}")
            print(f"✅ Productos de inventario (INVENTORY): {inventory_count}")
            print(f"⚠️ Productos sin tipo: {sin_tipo_count}")
            
            print("\n🎉 Actualización completada!")
            
        except Exception as e:
            print(f"❌ Error en actualización: {e}")
            db.rollback()
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
    update_product_types()


