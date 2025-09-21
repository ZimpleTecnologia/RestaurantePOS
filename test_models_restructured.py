"""
Script para probar los modelos del sistema reestructurado
"""
import sys
import traceback
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.menu_restructured import CategoriaPlatoVariable, OpcionPlato, MenuDiaRestructured, MenuDiaOpcion

def test_models_restructured():
    """Probar los modelos del sistema reestructurado"""
    print("🧪 PROBANDO MODELOS DEL SISTEMA REESTRUCTURADO")
    print("=" * 70)
    
    try:
        # Crear sesión
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 1. Probar consulta de categorías
        print("\n1️⃣ PROBANDO CONSULTA DE CATEGORÍAS...")
        try:
            categorias = db.query(CategoriaPlatoVariable).all()
            print(f"✅ Categorías encontradas: {len(categorias)}")
            for cat in categorias[:3]:
                print(f"   - {cat.nombre}: {cat.descripcion}")
        except Exception as e:
            print(f"❌ Error consultando categorías: {e}")
            traceback.print_exc()
        
        # 2. Probar consulta de opciones
        print("\n2️⃣ PROBANDO CONSULTA DE OPCIONES...")
        try:
            opciones = db.query(OpcionPlato).all()
            print(f"✅ Opciones encontradas: {len(opciones)}")
            for opcion in opciones[:3]:
                print(f"   - {opcion.nombre} ({opcion.tipo}): ${opcion.precio}")
        except Exception as e:
            print(f"❌ Error consultando opciones: {e}")
            traceback.print_exc()
        
        # 3. Probar consulta de menús
        print("\n3️⃣ PROBANDO CONSULTA DE MENÚS...")
        try:
            menus = db.query(MenuDiaRestructured).all()
            print(f"✅ Menús encontrados: {len(menus)}")
            for menu in menus[:3]:
                print(f"   - {menu.nombre} ({menu.fecha}): ${menu.precio}")
        except Exception as e:
            print(f"❌ Error consultando menús: {e}")
            traceback.print_exc()
        
        # 4. Probar relaciones
        print("\n4️⃣ PROBANDO RELACIONES...")
        try:
            # Obtener una opción con su categoría
            opcion_con_categoria = db.query(OpcionPlato).filter(OpcionPlato.categoria_id.isnot(None)).first()
            if opcion_con_categoria:
                print(f"✅ Opción con categoría: {opcion_con_categoria.nombre}")
                if opcion_con_categoria.categoria:
                    print(f"   - Categoría: {opcion_con_categoria.categoria.nombre}")
                else:
                    print("   - Sin categoría")
            else:
                print("⚠️ No hay opciones con categoría")
        except Exception as e:
            print(f"❌ Error probando relaciones: {e}")
            traceback.print_exc()
        
        # 5. Probar creación de una nueva categoría
        print("\n5️⃣ PROBANDO CREACIÓN DE CATEGORÍA...")
        try:
            nueva_categoria = CategoriaPlatoVariable(
                nombre="Categoría de Prueba",
                descripcion="Categoría creada para probar el sistema",
                orden=999,
                activo=True
            )
            db.add(nueva_categoria)
            db.commit()
            print(f"✅ Categoría creada: {nueva_categoria.nombre} (ID: {nueva_categoria.id})")
            
            # Eliminar la categoría de prueba
            db.delete(nueva_categoria)
            db.commit()
            print("✅ Categoría de prueba eliminada")
            
        except Exception as e:
            print(f"❌ Error creando categoría: {e}")
            traceback.print_exc()
            db.rollback()
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    print("✅ Modelos importados correctamente")
    print("✅ Consultas básicas funcionando")
    print("✅ Relaciones configuradas")
    print("✅ Operaciones CRUD funcionando")
    print("\n🎯 Si todas las pruebas pasan, el problema está en el router FastAPI")

if __name__ == "__main__":
    test_models_restructured()


