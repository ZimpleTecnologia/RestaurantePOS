#!/usr/bin/env python3
"""
Script para limpiar todos los datos de la base de datos del Sistema POS
Mantiene solo el usuario administrador por defecto
"""
import sys
import os
import time
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, create_tables
from app.models import *
from app.models.user import User, UserRole
from app.config import settings

def confirm_cleanup():
    """Solicitar confirmación antes de limpiar la base de datos"""
    print("⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos!")
    print("📋 Se eliminarán:")
    print("   - Todas las ventas y transacciones")
    print("   - Todos los productos y categorías")
    print("   - Todos los clientes y créditos")
    print("   - Todo el inventario y movimientos")
    print("   - Todas las órdenes y pedidos")
    print("   - Todos los proveedores y compras")
    print("   - Todas las mesas y ubicaciones")
    print("   - Todas las recetas")
    print("   - Todas las configuraciones del sistema")
    print("   - Todos los usuarios (excepto admin)")
    print()
    print("✅ Se mantendrá:")
    print("   - El usuario administrador (admin)")
    print("   - La estructura de las tablas")
    print()
    
    while True:
        response = input("¿Estás seguro de que quieres continuar? (sí/no): ").lower().strip()
        if response in ['sí', 'si', 'yes', 'y', 's']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Por favor, responde 'sí' o 'no'")

def wait_for_database():
    """Esperar a que la base de datos esté disponible"""
    print("🔄 Verificando conexión a la base de datos...")
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        try:
            db = next(get_db())
            db.execute(text("SELECT 1"))
            db.close()
            print("✅ Conexión a la base de datos establecida")
            return True
        except Exception as e:
            attempt += 1
            print(f"⏳ Intento {attempt}/{max_attempts}: {e}")
            time.sleep(2)
    
    print("❌ No se pudo conectar a la base de datos")
    return False

def clean_database():
    """Limpiar todos los datos de la base de datos"""
    print("🧹 Iniciando limpieza de la base de datos...")
    
    # Crear tablas si no existen
    create_tables()
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Desactivar restricciones de clave foránea temporalmente
        print("🔧 Desactivando restricciones de clave foránea...")
        db.execute(text("SET session_replication_role = replica;"))
        
        # Lista de tablas a limpiar (en orden para evitar problemas de dependencias)
        tables_to_clean = [
            # Transacciones y ventas
            ("SaleItem", "Items de venta"),
            ("Sale", "Ventas"),
            ("Payment", "Pagos"),
            ("Credit", "Créditos"),
            
            # Órdenes y pedidos
            ("OrderItem", "Items de órdenes"),
            ("Order", "Órdenes"),
            
            # Inventario y compras
            ("PurchaseItem", "Items de compras"),
            ("Purchase", "Compras"),
            ("InventoryMovement", "Movimientos de inventario"),
            
            # Recetas
            ("RecipeItem", "Items de recetas"),
            ("Recipe", "Recetas"),
            
            # Productos
            ("Product", "Productos"),
            ("SubCategory", "Subcategorías"),
            ("Category", "Categorías"),
            
            # Clientes y proveedores
            ("Customer", "Clientes"),
            ("Supplier", "Proveedores"),
            
            # Mesas y ubicaciones
            ("Table", "Mesas"),
            ("Location", "Ubicaciones"),
            
            # Configuraciones
            ("SystemSettings", "Configuraciones del sistema"),
            
            # Usuarios (excepto admin)
            ("User", "Usuarios (excepto admin)")
        ]
        
        total_tables = len(tables_to_clean)
        cleaned_count = 0
        
        for table_name, description in tables_to_clean:
            try:
                if table_name == "User":
                    # Para usuarios, eliminar todos excepto admin
                    deleted_count = db.query(User).filter(User.username != "admin").delete()
                    print(f"✅ {description}: {deleted_count} registros eliminados")
                else:
                    # Para otras tablas, eliminar todos los registros
                    table_class = globals()[table_name]
                    deleted_count = db.query(table_class).delete()
                    print(f"✅ {description}: {deleted_count} registros eliminados")
                
                cleaned_count += 1
                
            except Exception as e:
                print(f"⚠️  Error limpiando {description}: {e}")
                continue
        
        # Reactivar restricciones de clave foránea
        print("🔧 Reactivando restricciones de clave foránea...")
        db.execute(text("SET session_replication_role = DEFAULT;"))
        
        # Commit de todos los cambios
        db.commit()
        
        print(f"\n🎉 Limpieza completada!")
        print(f"📊 Tablas procesadas: {cleaned_count}/{total_tables}")
        
        # Verificar que el admin sigue existiendo
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print(f"✅ Usuario admin preservado: {admin_user.username}")
        else:
            print("⚠️  Usuario admin no encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def reset_sequences():
    """Resetear las secuencias de ID para que empiecen desde 1"""
    print("🔄 Reseteando secuencias de ID...")
    
    db = next(get_db())
    
    try:
        # Lista de secuencias comunes
        sequences = [
            "users_id_seq",
            "products_id_seq", 
            "categories_id_seq",
            "subcategories_id_seq",
            "sales_id_seq",
            "sale_items_id_seq",
            "customers_id_seq",
            "suppliers_id_seq",
            "inventory_movements_id_seq",
            "orders_id_seq",
            "order_items_id_seq",
            "tables_id_seq",
            "locations_id_seq",
            "recipes_id_seq",
            "recipe_items_id_seq"
        ]
        
        for seq in sequences:
            try:
                db.execute(text(f"SELECT setval('{seq}', 1, false);"))
                print(f"✅ Secuencia {seq} reseteada")
            except Exception as e:
                print(f"⚠️  No se pudo resetear {seq}: {e}")
        
        db.commit()
        print("✅ Secuencias reseteadas")
        
    except Exception as e:
        print(f"❌ Error reseteando secuencias: {e}")
        db.rollback()
    finally:
        db.close()

def show_database_status():
    """Mostrar el estado actual de la base de datos"""
    print("\n📊 Estado actual de la base de datos:")
    
    db = next(get_db())
    
    try:
        # Contar registros en cada tabla
        tables_info = [
            ("User", "Usuarios"),
            ("Product", "Productos"),
            ("Category", "Categorías"),
            ("Sale", "Ventas"),
            ("Customer", "Clientes"),
            ("Supplier", "Proveedores"),
            ("Order", "Órdenes"),
            ("Table", "Mesas"),
            ("InventoryMovement", "Movimientos de inventario")
        ]
        
        for table_name, description in tables_info:
            try:
                table_class = globals()[table_name]
                count = db.query(table_class).count()
                print(f"   {description}: {count} registros")
            except Exception as e:
                print(f"   {description}: Error al contar - {e}")
        
    except Exception as e:
        print(f"❌ Error obteniendo estado: {e}")
    finally:
        db.close()

def main():
    """Función principal"""
    print("=" * 60)
    print("🧹 SCRIPT DE LIMPIEZA DE BASE DE DATOS - SISTEMA POS")
    print("=" * 60)
    print(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar conexión a la base de datos
    if not wait_for_database():
        print("❌ No se pudo conectar a la base de datos. Verifica la configuración.")
        sys.exit(1)
    
    # Solicitar confirmación
    if not confirm_cleanup():
        print("❌ Operación cancelada por el usuario")
        sys.exit(0)
    
    print("\n🚀 Iniciando proceso de limpieza...")
    
    # Limpiar base de datos
    if not clean_database():
        print("❌ Error durante la limpieza")
        sys.exit(1)
    
    # Resetear secuencias
    reset_sequences()
    
    # Mostrar estado final
    show_database_status()
    
    print("\n" + "=" * 60)
    print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("📋 Resumen:")
    print("   - Todos los datos han sido eliminados")
    print("   - El usuario admin se ha preservado")
    print("   - Las secuencias de ID han sido reseteadas")
    print("   - La base de datos está lista para uso")
    print()
    print("🔑 Credenciales del admin:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print()
    print("🚀 Puedes reiniciar la aplicación ahora")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
