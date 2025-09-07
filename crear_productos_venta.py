#!/usr/bin/env python3
"""
Script para crear productos de venta (platos) de ejemplo
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

def crear_productos_venta():
    """Crear productos de venta de ejemplo"""
    try:
        # Configurar conexión a la base de datos
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/restaurante_pos")
        engine = create_engine(database_url)
        
        print("🍽️ Creando productos de venta (platos)...")
        print("=" * 50)
        
        with engine.connect() as conn:
            # Iniciar transacción
            trans = conn.begin()
            
            try:
                # Obtener categoría "PLATO_PRINCIPAL"
                result = conn.execute(text("""
                    SELECT id FROM products 
                    WHERE category = 'PLATO_PRINCIPAL' 
                    LIMIT 1
                """)).fetchone()
                
                categoria_id = result[0] if result else None
                
                if not categoria_id:
                    print("❌ No se encontró categoría PLATO_PRINCIPAL")
                    return False
                
                # Productos de venta a crear
                productos_venta = [
                    {
                        "nombre": "Costilla en Salsa BBQ",
                        "codigo": "COST001",
                        "precio": 25000,
                        "descripcion": "Costilla de cerdo marinada en salsa BBQ casera, acompañada de papas a la francesa",
                        "categoria_id": categoria_id,
                        "unidad": "porción"
                    },
                    {
                        "nombre": "Pollo a la Plancha",
                        "codigo": "POLL001", 
                        "precio": 18000,
                        "descripcion": "Pechuga de pollo a la plancha con especias, acompañada de arroz y ensalada",
                        "categoria_id": categoria_id,
                        "unidad": "porción"
                    },
                    {
                        "nombre": "Carne Asada",
                        "codigo": "CARN001",
                        "precio": 22000,
                        "descripcion": "Carne de res asada con chimichurri, acompañada de papas y vegetales",
                        "categoria_id": categoria_id,
                        "unidad": "porción"
                    },
                    {
                        "nombre": "Arroz con Pollo",
                        "codigo": "ARRO001",
                        "precio": 15000,
                        "descripcion": "Arroz con pollo, verduras y especias, plato tradicional",
                        "categoria_id": categoria_id,
                        "unidad": "porción"
                    },
                    {
                        "nombre": "Ensalada César",
                        "codigo": "ENSA001",
                        "precio": 12000,
                        "descripcion": "Lechuga fresca con aderezo césar, crutones y queso parmesano",
                        "categoria_id": categoria_id,
                        "unidad": "porción"
                    }
                ]
                
                productos_creados = 0
                
                for producto in productos_venta:
                    # Verificar si el producto ya existe
                    result = conn.execute(text("""
                        SELECT id FROM products WHERE code = :codigo
                    """), {"codigo": producto["codigo"]}).fetchone()
                    
                    if result:
                        print(f"   ⚠️  {producto['nombre']}: Ya existe (ID: {result[0]})")
                        continue
                    
                    # Crear el producto
                    conn.execute(text("""
                        INSERT INTO products 
                        (name, code, description, price, product_type, category_id, 
                         stock_quantity, min_stock_level, max_stock_level, stock, min_stock, max_stock,
                         unit, is_active, created_at)
                        VALUES 
                        (:nombre, :codigo, :descripcion, :precio, 'SALES', :categoria_id,
                         0, 0, 100, 0, 0, 100, :unidad, true, :fecha)
                    """), {
                        "nombre": producto["nombre"],
                        "codigo": producto["codigo"],
                        "descripcion": producto["descripcion"],
                        "precio": producto["precio"],
                        "categoria_id": categoria_id,
                        "unidad": producto["unidad"],
                        "fecha": datetime.now()
                    })
                    
                    productos_creados += 1
                    print(f"   ✅ {producto['nombre']}: Creado exitosamente")
                
                # Confirmar transacción
                trans.commit()
                print(f"\n✅ Productos de venta creados: {productos_creados}")
                
                # Mostrar resumen
                result = conn.execute(text("""
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN product_type = 'SALES' THEN 1 ELSE 0 END) as ventas,
                           SUM(CASE WHEN product_type = 'INVENTORY' THEN 1 ELSE 0 END) as inventario
                    FROM products 
                    WHERE is_active = true
                """)).fetchone()
                
                print(f"\n📊 Resumen de productos:")
                print(f"   Total activos: {result[0]}")
                print(f"   Productos de venta: {result[1]}")
                print(f"   Productos de inventario: {result[2]}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error durante la creación: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    crear_productos_venta()
