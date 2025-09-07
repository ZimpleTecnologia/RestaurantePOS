#!/usr/bin/env python3
"""
Script para limpiar sesiones de caja directamente
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.cash_register import CashSession, CashStatus
from sqlalchemy import and_
from datetime import date

def limpiar_sesiones():
    """Limpiar sesiones de caja"""
    print("=" * 60)
    print("🧹 LIMPIAR SESIONES DE CAJA")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. Verificar sesiones activas
        print("\n1️⃣ Verificando sesiones activas...")
        active_sessions = db.query(CashSession).filter(
            CashSession.status == CashStatus.OPEN
        ).all()
        
        print(f"   Sesiones activas encontradas: {len(active_sessions)}")
        
        for session in active_sessions:
            print(f"   - ID: {session.id}, Número: {session.session_number}")
            print(f"     Abierta: {session.opened_at}")
            print(f"     Usuario: {session.user.full_name if session.user else 'N/A'}")
        
        # 2. Cerrar sesiones activas
        if active_sessions:
            print("\n2️⃣ Cerrando sesiones activas...")
            for session in active_sessions:
                session.status = CashStatus.CLOSED
                session.closed_at = session.opened_at  # Usar la misma fecha
                session.closing_amount = session.opening_amount  # Usar el mismo monto
                session.closing_notes = "Cierre automático desde script"
                print(f"   ✅ Sesión {session.session_number} cerrada")
            
            db.commit()
            print(f"   ✅ {len(active_sessions)} sesiones cerradas")
        else:
            print("\n2️⃣ No hay sesiones activas para cerrar")
        
        # 3. Verificar estado final
        print("\n3️⃣ Verificando estado final...")
        remaining_active = db.query(CashSession).filter(
            CashSession.status == CashStatus.OPEN
        ).count()
        
        print(f"   Sesiones activas restantes: {remaining_active}")
        
        if remaining_active == 0:
            print("   ✅ Todas las sesiones han sido cerradas")
        else:
            print("   ⚠️ Aún hay sesiones activas")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("✅ Limpieza completada")

if __name__ == "__main__":
    limpiar_sesiones()
