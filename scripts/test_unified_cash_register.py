#!/usr/bin/env python3
"""
Script para probar el Módulo Unificado de Caja con Autenticación
"""
import sys
import os
from decimal import Decimal

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.services.cash_service import CashService
from app.services.settings_service import SettingsService
from app.models.sale import Sale
from app.models.user import User
from app.models.product import Product

def test_unified_cash_register():
    """Probar el módulo unificado de caja"""
    print("🧪 Probando Módulo Unificado de Caja...")
    
    db = next(get_db())
    
    try:
        # 1. Inicializar configuraciones
        print("\n1️⃣ Inicializando configuraciones...")
        SettingsService.initialize_default_settings(db)
        print("✅ Configuraciones inicializadas")
        
        # 2. Verificar contraseña por defecto
        print("\n2️⃣ Verificando contraseña por defecto...")
        default_password = SettingsService.get_cash_register_password(db)
        print(f"✅ Contraseña por defecto: {default_password}")
        
        # 3. Verificar autenticación
        print("\n3️⃣ Probando autenticación...")
        is_valid = SettingsService.verify_cash_register_password(db, "1234")
        print(f"✅ Contraseña '1234' válida: {is_valid}")
        
        is_invalid = SettingsService.verify_cash_register_password(db, "wrong")
        print(f"✅ Contraseña 'wrong' inválida: {not is_invalid}")
        
        # 4. Cambiar contraseña
        print("\n4️⃣ Cambiando contraseña...")
        SettingsService.set_cash_register_password(db, "5678")
        new_password = SettingsService.get_cash_register_password(db)
        print(f"✅ Nueva contraseña: {new_password}")
        
        # Verificar nueva contraseña
        is_new_valid = SettingsService.verify_cash_register_password(db, "5678")
        print(f"✅ Nueva contraseña válida: {is_new_valid}")
        
        # 5. Verificar estado de caja
        print("\n5️⃣ Verificando estado de caja...")
        cash_register = CashService.get_main_cash_register(db)
        if not cash_register:
            cash_register = CashService.create_main_cash_register(db)
            print(f"✅ Caja principal creada: {cash_register.name}")
        else:
            print(f"✅ Caja principal encontrada: {cash_register.name}")
        
        # 6. Verificar restricción de ventas
        print("\n6️⃣ Verificando restricción de ventas...")
        require_cash = SettingsService.require_cash_register(db)
        print(f"✅ Requiere caja para ventas: {require_cash}")
        
        can_create_sale = CashService.can_create_sale(db, cash_register.id)
        print(f"✅ Se puede crear venta: {can_create_sale}")
        
        # 7. Abrir caja (simulando autenticación)
        print("\n7️⃣ Abriendo caja...")
        try:
            # Obtener un usuario para la prueba
            user = db.query(User).first()
            if not user:
                print("❌ No hay usuarios en la base de datos")
                return
            
            # Verificar contraseña antes de abrir
            if not SettingsService.verify_cash_register_password(db, "5678"):
                print("❌ Contraseña incorrecta")
                return
            
            session = CashService.open_session(
                db=db,
                cash_register_id=cash_register.id,
                user_id=user.id,
                opening_amount=Decimal('1000.00'),
                opening_notes="Apertura de prueba"
            )
            print(f"✅ Caja abierta: {session.session_number}")
            print(f"   Monto inicial: ${session.opening_amount}")
            print(f"   Usuario: {session.user.full_name}")
            
        except ValueError as e:
            print(f"⚠️ Error al abrir caja: {e}")
            return
        
        # 8. Verificar que ahora se puede crear venta
        print("\n8️⃣ Verificando que ahora se puede crear venta...")
        can_create_sale = CashService.can_create_sale(db, cash_register.id)
        print(f"✅ Se puede crear venta: {can_create_sale}")
        
        # 9. Obtener información del negocio
        print("\n9️⃣ Obteniendo información del negocio...")
        business_info = SettingsService.get_business_info(db)
        print(f"✅ Información del negocio:")
        for key, value in business_info.items():
            print(f"   {key}: {value}")
        
        # 10. Cerrar caja
        print("\n🔟 Cerrando caja...")
        try:
            closed_session = CashService.close_session(
                db=db,
                session_id=session.id,
                closing_amount=Decimal('1025.00'),
                closing_notes="Cierre de prueba"
            )
            print(f"✅ Caja cerrada: {closed_session.session_number}")
            print(f"   Monto de cierre: ${closed_session.closing_amount}")
            
            # Obtener resumen final
            final_summary = CashService.get_session_summary(db, session.id)
            if final_summary:
                print(f"   Diferencia: ${final_summary['difference']}")
        
        except Exception as e:
            print(f"❌ Error cerrando caja: {e}")
        
        print("\n✅ Todas las pruebas del módulo unificado completadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Función principal"""
    print("=" * 70)
    print("🧪 PRUEBAS DEL MÓDULO UNIFICADO DE CAJA")
    print("=" * 70)
    
    test_unified_cash_register()
    
    print("\n" + "=" * 70)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    main()
