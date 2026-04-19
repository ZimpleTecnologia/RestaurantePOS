"""
Script para poblar permisos iniciales del sistema
Ejecutar después de crear las tablas
"""
from app.database import SessionLocal
from app.models.permiso import Permiso
from app.models.user import User, UserRole


def seed_permisos():
    """Crea los permisos iniciales del sistema"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen permisos
        if db.query(Permiso).count() > 0:
            print("⚠️  Ya existen permisos en la base de datos")
            return
        
        # Permisos por módulo
        permisos_iniciales = [
            # Módulo Mesas
            {"codigo": "mesas", "nombre": "Gestión de Mesas", "descripcion": "Acceso completo al módulo de mesas", "modulo": "administracion"},
            {"codigo": "mesas_crear", "nombre": "Crear Mesas", "descripcion": "Crear nuevas mesas", "modulo": "administracion"},
            {"codigo": "mesas_editar", "nombre": "Editar Mesas", "descripcion": "Modificar mesas existentes", "modulo": "administracion"},
            {"codigo": "mesas_eliminar", "nombre": "Eliminar Mesas", "descripcion": "Eliminar mesas", "modulo": "administracion"},
            
            # Módulo Usuarios
            {"codigo": "usuarios", "nombre": "Gestión de Usuarios", "descripcion": "Acceso completo al módulo de usuarios", "modulo": "administracion"},
            {"codigo": "usuarios_crear", "nombre": "Crear Usuarios", "descripcion": "Crear nuevos usuarios", "modulo": "administracion"},
            {"codigo": "usuarios_editar", "nombre": "Editar Usuarios", "descripcion": "Modificar usuarios", "modulo": "administracion"},
            {"codigo": "usuarios_eliminar", "nombre": "Eliminar Usuarios", "descripcion": "Eliminar usuarios", "modulo": "administracion"},
            
            # Módulo Permisos
            {"codigo": "permisos", "nombre": "Gestión de Permisos", "descripcion": "Acceso completo al módulo de permisos", "modulo": "administracion"},
            {"codigo": "permisos_asignar", "nombre": "Asignar Permisos", "descripcion": "Asignar permisos a usuarios", "modulo": "administracion"},
            
            # Módulo Meseros
            {"codigo": "meseros", "nombre": "Gestión de Meseros", "descripcion": "Acceso al módulo de meseros", "modulo": "operaciones"},
            {"codigo": "meseros_pedidos", "nombre": "Tomar Pedidos", "descripcion": "Crear y gestionar pedidos", "modulo": "operaciones"},
            
            # Módulo Cocina
            {"codigo": "cocina", "nombre": "Gestión de Cocina", "descripcion": "Acceso completo al módulo de cocina", "modulo": "operaciones"},
            {"codigo": "cocina_ver_pedidos", "nombre": "Ver Pedidos Cocina", "descripcion": "Visualizar pedidos de cocina", "modulo": "operaciones"},
            {"codigo": "cocina_actualizar", "nombre": "Actualizar Estado Pedidos", "descripcion": "Cambiar estado de pedidos", "modulo": "operaciones"},
            
            # Módulo Ventas
            {"codigo": "ventas", "nombre": "Gestión de Ventas", "descripcion": "Acceso completo al módulo de ventas", "modulo": "financiero"},
            {"codigo": "ventas_crear", "nombre": "Registrar Ventas", "descripcion": "Crear nuevas ventas", "modulo": "financiero"},
            {"codigo": "ventas_anular", "nombre": "Anular Ventas", "descripcion": "Anular ventas existentes", "modulo": "financiero"},
            
            # Módulo Caja
            {"codigo": "caja", "nombre": "Gestión de Caja", "descripcion": "Acceso completo al módulo de caja", "modulo": "financiero"},
            {"codigo": "caja_abrir", "nombre": "Abrir Caja", "descripcion": "Abrir turno de caja", "modulo": "financiero"},
            {"codigo": "caja_cerrar", "nombre": "Cerrar Caja", "descripcion": "Cerrar y arquear caja", "modulo": "financiero"},
            
            # Módulo Inventario
            {"codigo": "inventario", "nombre": "Gestión de Inventario", "descripcion": "Acceso completo al inventario", "modulo": "almacen"},
            {"codigo": "inventario_crear", "nombre": "Crear Productos", "descripcion": "Agregar nuevos productos", "modulo": "almacen"},
            {"codigo": "inventario_editar", "nombre": "Editar Productos", "descripcion": "Modificar productos", "modulo": "almacen"},
            {"codigo": "inventario_movimientos", "nombre": "Movimientos de Inventario", "descripcion": "Registrar entradas/salidas", "modulo": "almacen"},
            
            # Módulo Reportes
            {"codigo": "reportes", "nombre": "Acceso a Reportes", "descripcion": "Ver todos los reportes", "modulo": "reportes"},
            {"codigo": "reportes_ventas", "nombre": "Reportes de Ventas", "descripcion": "Ver reportes de ventas", "modulo": "reportes"},
            {"codigo": "reportes_inventario", "nombre": "Reportes de Inventario", "descripcion": "Ver reportes de inventario", "modulo": "reportes"},
            {"codigo": "reportes_financieros", "nombre": "Reportes Financieros", "descripcion": "Ver reportes financieros", "modulo": "reportes"},
        ]
        
        # Crear permisos
        for permiso_data in permisos_iniciales:
            permiso = Permiso(**permiso_data)
            db.add(permiso)
        
        db.commit()
        print(f"✅ {len(permisos_iniciales)} permisos creados exitosamente")
        
        # Verificar usuarios ADMIN (sin intentar acceder a columnas que podrían no existir)
        try:
            admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
            if admin_count > 0:
                print(f"📌 Se encontraron {admin_count} usuario(s) ADMIN")
                # Los admin ya tienen todos los permisos automáticamente por lógica
                print("✅ Usuarios ADMIN tienen acceso completo automático")
            else:
                print("⚠️  No se encontró ningún usuario ADMIN")
                print("💡 Crea un usuario ADMIN desde la aplicación para gestionar permisos")
        except Exception as e:
            print(f"⚠️  No se pudo verificar usuarios ADMIN: {str(e)}")
            print("✅ Los permisos se crearon correctamente de todas formas")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear permisos: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Poblando permisos iniciales...")
    seed_permisos()
    print("✅ Proceso completado")

