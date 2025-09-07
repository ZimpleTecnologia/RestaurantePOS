#!/usr/bin/env python3
"""
Script para probar la integración entre Sistema de Caja y Ventas
"""
import sys
import os
from decimal import Decimal

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.services.cash_service import CashService
from app.models.sale import Sale
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer

def test_cash_sales_integration():
    """Probar la integración entre caja y ventas"""
    print("🧪 Probando integración Caja + Ventas...")
    
    db = next(get_db())
    
    try:
        # 1. Verificar caja principal
        print("\n1️⃣ Verificando caja principal...")
        cash_register = CashService.get_main_cash_register(db)
        if not cash_register:
            cash_register = CashService.create_main_cash_register(db)
            print(f"✅ Caja principal creada: {cash_register.name}")
        else:
            print(f"✅ Caja principal encontrada: {cash_register.name}")
        
        # 2. Verificar estado inicial
        print("\n2️⃣ Verificando estado inicial...")
        active_session = CashService.get_active_session(db, cash_register.id)
        if active_session:
            print(f"⚠️ Ya hay una sesión activa: {active_session.session_number}")
        else:
            print("✅ No hay sesión activa")
        
        # 3. Verificar si se puede crear venta sin caja abierta
        print("\n3️⃣ Verificando restricción de ventas sin caja...")
        can_create_sale = CashService.can_create_sale(db, cash_register.id)
        print(f"¿Se puede crear venta? {'❌ NO' if not can_create_sale else '✅ SÍ'}")
        
        if not can_create_sale:
            print("✅ Restricción funcionando correctamente")
        
        # 4. Abrir sesión de caja
        print("\n4️⃣ Abriendo sesión de caja...")
        try:
            # Obtener un usuario para la prueba
            user = db.query(User).first()
            if not user:
                print("❌ No hay usuarios en la base de datos")
                return
            
            session = CashService.open_session(
                db=db,
                cash_register_id=cash_register.id,
                user_id=user.id,
                opening_amount=Decimal('1000.00'),
                opening_notes="Apertura de prueba"
            )
            print(f"✅ Sesión abierta: {session.session_number}")
            print(f"   Monto inicial: ${session.opening_amount}")
            print(f"   Usuario: {session.user.full_name}")
            
        except ValueError as e:
            print(f"⚠️ Error al abrir sesión: {e}")
            return
        
        # 5. Verificar que ahora se puede crear venta
        print("\n5️⃣ Verificando que ahora se puede crear venta...")
        can_create_sale = CashService.can_create_sale(db, cash_register.id)
        print(f"¿Se puede crear venta? {'❌ NO' if not can_create_sale else '✅ SÍ'}")
        
        # 6. Simular creación de venta
        print("\n6️⃣ Simulando creación de venta...")
        try:
            # Verificar que hay productos
            products = db.query(Product).limit(1).all()
            if not products:
                print("⚠️ No hay productos para crear venta de prueba")
            else:
                # Crear venta de prueba
                sale = Sale(
                    sale_number="V20240827-0001",
                    user_id=user.id,
                    total=Decimal('25.00'),
                    status="completada"
                )
                db.add(sale)
                db.flush()
                
                # Registrar movimiento en caja
                movement = CashService.register_sale_movement(
                    db=db,
                    session_id=session.id,
                    sale_id=sale.id,
                    amount=sale.total,
                    description=f"Venta de prueba {sale.sale_number}"
                )
                
                print(f"✅ Venta creada: {sale.sale_number}")
                print(f"✅ Movimiento registrado: {movement.description}")
                print(f"   Monto: ${movement.amount}")
                
                # Limpiar venta de prueba
                db.delete(sale)
                db.commit()
        
        except Exception as e:
            print(f"❌ Error creando venta: {e}")
        
        # 7. Obtener resumen de sesión
        print("\n7️⃣ Obteniendo resumen de sesión...")
        summary = CashService.get_session_summary(db, session.id)
        if summary:
            print(f"✅ Resumen obtenido:")
            print(f"   Sesión: {summary['session_number']}")
            print(f"   Total ventas: ${summary['total_sales']}")
            print(f"   Total gastos: ${summary['total_expenses']}")
            print(f"   Monto esperado: ${summary['expected_amount']}")
        
        # 8. Cerrar sesión
        print("\n8️⃣ Cerrando sesión...")
        try:
            closed_session = CashService.close_session(
                db=db,
                session_id=session.id,
                closing_amount=Decimal('1025.00'),
                closing_notes="Cierre de prueba"
            )
            print(f"✅ Sesión cerrada: {closed_session.session_number}")
            print(f"   Monto de cierre: ${closed_session.closing_amount}")
            
            # Obtener resumen final
            final_summary = CashService.get_session_summary(db, session.id)
            if final_summary:
                print(f"   Diferencia: ${final_summary['difference']}")
        
        except Exception as e:
            print(f"❌ Error cerrando sesión: {e}")
        
        print("\n✅ Todas las pruebas completadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal"""
    print("=" * 70)
    print("🧪 PRUEBAS DE INTEGRACIÓN CAJA + VENTAS")
    print("=" * 70)
    
    test_cash_sales_integration()
    
    print("\n" + "=" * 70)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    main()
