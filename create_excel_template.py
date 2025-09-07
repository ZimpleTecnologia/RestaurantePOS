#!/usr/bin/env python3
"""
Script para crear una plantilla Excel de ejemplo para la carga de inventario
"""
import pandas as pd
from datetime import datetime, timedelta

def create_inventory_template():
    """Crear plantilla Excel para carga de inventario"""
    
    # Datos de ejemplo
    sample_data = [
        {
            'nombre': 'Hamburguesa Clásica',
            'precio': 12.50,
            'categoria_id': 1,
            'stock_actual': 50,
            'precio_compra': 8.00,
            'descripcion': 'Hamburguesa con carne, lechuga, tomate y queso',
            'codigo_barras': '1234567890123',
            'sku': 'HAMB001',
            'punto_reorden': 10,
            'cantidad_reorden': 30,
            'unidad_medida': 'unidades',
            'peso': 0.3,
            'dimensiones': '15x10x5 cm',
            'ubicacion_default': 'Refrigerador',
            'fecha_vencimiento': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'lote': 'LOT001',
            'proveedor': 'Carnes Premium'
        },
        {
            'nombre': 'Coca Cola 500ml',
            'precio': 2.50,
            'categoria_id': 2,
            'stock_actual': 100,
            'precio_compra': 1.80,
            'descripcion': 'Refresco Coca Cola 500ml',
            'codigo_barras': '1234567890124',
            'sku': 'BEB001',
            'punto_reorden': 20,
            'cantidad_reorden': 50,
            'unidad_medida': 'unidades',
            'peso': 0.5,
            'dimensiones': '8x8x15 cm',
            'ubicacion_default': 'Refrigerador',
            'fecha_vencimiento': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
            'lote': 'LOT002',
            'proveedor': 'Coca Cola'
        },
        {
            'nombre': 'Papas Fritas',
            'precio': 4.00,
            'categoria_id': 1,
            'stock_actual': 75,
            'precio_compra': 2.50,
            'descripcion': 'Papas fritas crujientes',
            'codigo_barras': '1234567890125',
            'sku': 'PAPAS001',
            'punto_reorden': 15,
            'cantidad_reorden': 40,
            'unidad_medida': 'porciones',
            'peso': 0.2,
            'dimensiones': '12x8x3 cm',
            'ubicacion_default': 'Almacén Seco',
            'fecha_vencimiento': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
            'lote': 'LOT003',
            'proveedor': 'Snacks Express'
        },
        {
            'nombre': 'Agua Mineral 500ml',
            'precio': 1.50,
            'categoria_id': 2,
            'stock_actual': 200,
            'precio_compra': 0.80,
            'descripcion': 'Agua mineral natural',
            'codigo_barras': '1234567890126',
            'sku': 'AGUA001',
            'punto_reorden': 30,
            'cantidad_reorden': 100,
            'unidad_medida': 'unidades',
            'peso': 0.5,
            'dimensiones': '6x6x15 cm',
            'ubicacion_default': 'Refrigerador',
            'fecha_vencimiento': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'lote': 'LOT004',
            'proveedor': 'Aguas Puras'
        },
        {
            'nombre': 'Tarta de Chocolate',
            'precio': 8.00,
            'categoria_id': 3,
            'stock_actual': 20,
            'precio_compra': 5.00,
            'descripcion': 'Tarta de chocolate casera',
            'codigo_barras': '1234567890127',
            'sku': 'TARTA001',
            'punto_reorden': 5,
            'cantidad_reorden': 15,
            'unidad_medida': 'porciones',
            'peso': 0.4,
            'dimensiones': '20x20x5 cm',
            'ubicacion_default': 'Refrigerador',
            'fecha_vencimiento': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'lote': 'LOT005',
            'proveedor': 'Pastelería Dulce'
        }
    ]
    
    # Crear DataFrame
    df = pd.DataFrame(sample_data)
    
    # Reordenar columnas para que las obligatorias estén primero
    column_order = [
        'nombre', 'precio', 'categoria_id', 'stock_actual', 'precio_compra',
        'descripcion', 'codigo_barras', 'sku', 'punto_reorden', 'cantidad_reorden',
        'unidad_medida', 'peso', 'dimensiones', 'ubicacion_default', 
        'fecha_vencimiento', 'lote', 'proveedor'
    ]
    
    df = df[column_order]
    
    # Crear archivo Excel
    filename = 'plantilla_inventario.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Hoja principal con datos
        df.to_excel(writer, sheet_name='Inventario', index=False)
        
        # Hoja con instrucciones
        instructions = [
            ['INSTRUCCIONES PARA CARGA DE INVENTARIO'],
            [''],
            ['CAMPOS OBLIGATORIOS:'],
            ['- nombre: Nombre del producto'],
            ['- precio: Precio de venta (número decimal)'],
            ['- categoria_id: ID de la categoría (1=Comida, 2=Bebida, 3=Postre, etc.)'],
            ['- stock_actual: Cantidad inicial en inventario (número entero)'],
            ['- precio_compra: Precio de compra (número decimal)'],
            [''],
            ['CAMPOS OPCIONALES:'],
            ['- descripcion: Descripción del producto'],
            ['- codigo_barras: Código de barras del producto'],
            ['- sku: Código SKU interno'],
            ['- punto_reorden: Cantidad mínima para reordenar'],
            ['- cantidad_reorden: Cantidad a ordenar cuando se alcanza el punto de reorden'],
            ['- unidad_medida: Unidad de medida (kg, litros, unidades, etc.)'],
            ['- peso: Peso del producto en kg'],
            ['- dimensiones: Dimensiones del producto'],
            ['- ubicacion_default: Nombre de la ubicación por defecto'],
            ['- fecha_vencimiento: Fecha de vencimiento (YYYY-MM-DD)'],
            ['- lote: Número de lote'],
            ['- proveedor: Nombre del proveedor'],
            [''],
            ['NOTAS IMPORTANTES:'],
            ['- La primera fila debe contener los nombres de las columnas'],
            ['- Los IDs de categoría deben existir en el sistema o se crearán automáticamente'],
            ['- Los productos existentes se actualizarán si tienen el mismo nombre'],
            ['- Se creará automáticamente un movimiento de stock inicial'],
            ['- Las fechas deben estar en formato YYYY-MM-DD'],
            ['- Los números decimales usan punto como separador (ej: 12.50)']
        ]
        
        instructions_df = pd.DataFrame(instructions)
        instructions_df.to_excel(writer, sheet_name='Instrucciones', index=False, header=False)
        
        # Hoja con categorías de ejemplo
        categories = [
            ['ID', 'Nombre', 'Descripción'],
            [1, 'Comida', 'Platos principales y acompañamientos'],
            [2, 'Bebida', 'Bebidas y refrescos'],
            [3, 'Postre', 'Postres y dulces'],
            [4, 'Entrada', 'Entradas y aperitivos'],
            [5, 'Especial', 'Platos especiales del día']
        ]
        
        categories_df = pd.DataFrame(categories[1:], columns=categories[0])
        categories_df.to_excel(writer, sheet_name='Categorías', index=False)
    
    print(f"Plantilla creada exitosamente: {filename}")
    print("Puedes usar este archivo como base para cargar tu inventario.")
    
    return filename

if __name__ == "__main__":
    create_inventory_template()
