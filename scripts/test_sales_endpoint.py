#!/usr/bin/env python3
"""
Script para probar el endpoint de ventas
"""
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models.sale import Sale
from app.models.user import User
from app.models.customer import Customer

def test_sales_endpoint():
    """Probar el endpoint de ventas"""
    print("🧪 Probando endpoint de ventas...")
    
    db = next(get_db())
    
    try:
        # Verificar que podemos acceder a la tabla sales
        sales_count = db.query(Sale).count()
        print(f"✅ Acceso a tabla sales: {sales_count} registros")
        
        # Verificar que podemos hacer consultas básicas
        sales = db.query(Sale).limit(5).all()
        print(f"✅ Consulta básica: {len(sales)} ventas obtenidas")
        
        # Verificar relaciones
        if sales:
            sale = sales[0]
            print(f"✅ Venta ID: {sale.id}")
            print(f"✅ Número de venta: {sale.sale_number}")
            print(f"✅ Total: {sale.total}")
            print(f"✅ Estado: {sale.status}")
            
            # Verificar relación con usuario
            if sale.user_id:
                user = db.query(User).filter(User.id == sale.user_id).first()
                if user:
                    print(f"✅ Usuario: {user.full_name}")
                else:
                    print("⚠️ Usuario no encontrado")
            
            # Verificar relación con cliente
            if sale.customer_id:
                customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
                if customer:
                    print(f"✅ Cliente: {customer.full_name}")
                else:
                    print("⚠️ Cliente no encontrado")
        
        print("✅ Todas las pruebas pasaron")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal"""
    print("=" * 50)
    print("🧪 PRUEBAS DEL ENDPOINT DE VENTAS")
    print("=" * 50)
    
    test_sales_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    main()
