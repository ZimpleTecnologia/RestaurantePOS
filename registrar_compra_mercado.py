#!/usr/bin/env python3
"""
Script para registrar compras del mercado en el inventario
"""
import sys
import os
from sqlalchemy import text, create_engine
from datetime import datetime

# Cargar variables de entorno desde .env si existe
from dotenv import load_dotenv
load_dotenv()

# Si no hay archivo .env, usar configuración por defecto
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://sistema_pos_user:sistema_pos_password@localhost:5432/sistema_pos"

def registrar_compra_mercado():
    """Registrar compras del mercado en el inventario"""
    try:
        # Crear conexión directa a la base de datos
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        
        print("🛒 Registro de Compras del Mercado")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                # Obtener categoría de materias primas
                result = conn.execute(text("""
                    SELECT id FROM categories 
                    WHERE name = 'Materias Primas' AND is_active = true
                """)).fetchone()
                
                if not result:
                    print("❌ Categoría 'Materias Primas' no encontrada")
                    return False
                
                categoria_id = result[0]
                print(f"✅ Usando categoría ID: {categoria_id}")
                
                # Obtener ubicación por defecto
                result = conn.execute(text("""
                    SELECT id FROM inventory_locations 
                    WHERE is_default = true AND is_active = true
                """)).fetchone()
                
                if not result:
                    print("❌ Ubicación por defecto no encontrada")
                    return False
                
                ubicacion_id = result[0]
                print(f"✅ Usando ubicación ID: {ubicacion_id}")
                
                # Lista de compras del mercado (ejemplo)
                compras_mercado = [
                    {
                        "nombre": "Arroz 10KG",
                        "codigo": "ARR001",
                        "precio_compra": 25.00,
                        "cantidad": 50,
                        "unidad": "kg",
                        "stock_minimo": 10
                    },
                    {
                        "nombre": "Pollo 40 porciones",
                        "codigo": "POL001", 
                        "precio_compra": 45.00,
                        "cantidad": 30,
                        "unidad": "porciones",
                        "stock_minimo": 5
                    },
                    {
                        "nombre": "Carne 50 porciones",
                        "codigo": "CAR001",
                        "precio_compra": 60.00,
                        "cantidad": 25,
                        "unidad": "porciones",
                        "stock_minimo": 8
                    },
                    {
                        "nombre": "Costilla Cerdo 2KG",
                        "codigo": "COS001",
                        "precio_compra": 35.00,
                        "cantidad": 15,
                        "unidad": "kg",
                        "stock_minimo": 3
                    },
                    {
                        "nombre": "Tomates 5KG",
                        "codigo": "TOM001",
                        "precio_compra": 15.00,
                        "cantidad": 20,
                        "unidad": "kg",
                        "stock_minimo": 5
                    },
                    {
                        "nombre": "Cebollas 3KG",
                        "codigo": "CEB001",
                        "precio_compra": 12.00,
                        "cantidad": 15,
                        "unidad": "kg",
                        "stock_minimo": 3
                    }
                ]
                
                print(f"\n📦 Registrando {len(compras_mercado)} productos del mercado...")
                
                productos_creados = 0
                productos_actualizados = 0
                
                for compra in compras_mercado:
                    # Verificar si el producto ya existe
                    result = conn.execute(text("""
                        SELECT id, stock_quantity FROM products 
                        WHERE code = :codigo AND is_active = true
                    """), {"codigo": compra["codigo"]}).fetchone()
                    
                    if result:
                        # Producto existe, actualizar stock
                        producto_id = result[0]
                        stock_actual = result[1]
                        nuevo_stock = stock_actual + compra["cantidad"]
                        
                        # Actualizar stock del producto
                        conn.execute(text("""
                            UPDATE products 
                            SET stock_quantity = :nuevo_stock,
                                purchase_price = :precio_compra
                            WHERE id = :producto_id
                        """), {
                            "nuevo_stock": nuevo_stock,
                            "precio_compra": compra["precio_compra"],
                            "producto_id": producto_id
                        })
                        
                        # Crear movimiento de inventario
                        conn.execute(text("""
                            INSERT INTO inventory_movements 
                            (product_id, user_id, adjustment_type, reason, quantity, 
                             previous_stock, new_stock, notes, created_at)
                            VALUES 
                            (:product_id, 1, 'entrada', 'compra_proveedor', :cantidad,
                             :stock_anterior, :nuevo_stock, :notas, :fecha)
                        """), {
                            "product_id": producto_id,
                            "cantidad": compra["cantidad"],
                            "stock_anterior": stock_actual,
                            "nuevo_stock": nuevo_stock,
                            "notas": f"Compra del mercado - {compra['nombre']}",
                            "fecha": datetime.now()
                        })
                        
                        productos_actualizados += 1
                        print(f"   ✅ {compra['nombre']}: Stock actualizado ({stock_actual} → {nuevo_stock} {compra['unidad']})")
                        
                    else:
                        # Producto no existe, crearlo
                        conn.execute(text("""
                            INSERT INTO products 
                            (name, code, product_type, category_id, purchase_price, 
                             stock_quantity, min_stock_level, unit, price, is_active, created_at)
                            VALUES 
                            (:nombre, :codigo, 'inventory', :categoria_id, :precio_compra,
                             :cantidad, :stock_minimo, :unidad, 0, true, :fecha)
                        """), {
                            "nombre": compra["nombre"],
                            "codigo": compra["codigo"],
                            "categoria_id": categoria_id,
                            "precio_compra": compra["precio_compra"],
                            "cantidad": compra["cantidad"],
                            "stock_minimo": compra["stock_minimo"],
                            "unidad": compra["unidad"],
                            "fecha": datetime.now()
                        })
                        
                        # Obtener el ID del producto recién creado
                        result = conn.execute(text("""
                            SELECT id FROM products WHERE code = :codigo
                        """), {"codigo": compra["codigo"]}).fetchone()
                        
                        producto_id = result[0]
                        
                        # Crear movimiento de inventario inicial
                        conn.execute(text("""
                            INSERT INTO inventory_movements 
                            (product_id, user_id, adjustment_type, reason, quantity, 
                             previous_stock, new_stock, notes, created_at)
                            VALUES 
                            (:product_id, 1, 'entrada', 'compra_proveedor', :cantidad,
                             0, :cantidad, :notas, :fecha)
                        """), {
                            "product_id": producto_id,
                            "cantidad": compra["cantidad"],
                            "notas": f"Compra inicial del mercado - {compra['nombre']}",
                            "fecha": datetime.now()
                        })
                        
                        productos_creados += 1
                        print(f"   🆕 {compra['nombre']}: Producto creado ({compra['cantidad']} {compra['unidad']})")
                
                # Confirmar transacción
                trans.commit()
                
                print(f"\n✅ Registro de compras completado:")
                print(f"   📦 Productos creados: {productos_creados}")
                print(f"   🔄 Productos actualizados: {productos_actualizados}")
                
                # Mostrar resumen del inventario
                print(f"\n📊 Resumen del inventario:")
                result = conn.execute(text("""
                    SELECT name, stock_quantity, unit, purchase_price,
                           (stock_quantity * purchase_price) as valor_total
                    FROM products 
                    WHERE product_type = 'inventory' AND is_active = true
                    ORDER BY name
                """)).fetchall()
                
                valor_total = 0
                for row in result:
                    nombre = row[0] or "Sin nombre"
                    stock = row[1] or 0
                    unidad = row[2] or "unidad"
                    precio = row[3] or 0
                    total_valor = float(stock) * float(precio)
                    valor_total += total_valor
                    print(f"   {nombre}: {stock} {unidad} - ${precio:.2f} c/u - Total: ${total_valor:.2f}")
                
                print(f"\n💰 Valor total del inventario: ${valor_total:.2f}")
                
                return True
                
            except Exception as e:
                try:
                    trans.rollback()
                except:
                    pass  # La transacción ya puede estar desasociada
                print(f"❌ Error durante el registro: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🛒 Sistema de Registro de Compras del Mercado")
    print("=" * 50)
    
    if registrar_compra_mercado():
        print("\n🎉 ¡Compras del mercado registradas exitosamente!")
        print("\n📋 Próximos pasos:")
        print("   1. Verificar el inventario en la aplicación")
        print("   2. Crear recetas para los platos del menú")
        print("   3. Probar el sistema de ventas")
        
        return True
    else:
        print("❌ Error registrando las compras")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
