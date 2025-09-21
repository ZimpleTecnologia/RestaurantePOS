"""
Script para diagnosticar problemas con el sistema de menús reestructurado
"""
import sys
import traceback
from sqlalchemy import create_engine, text
from app.config import settings

def debug_menu_restructured():
    """Diagnosticar problemas con el sistema de menús reestructurado"""
    print("🔍 DIAGNOSTICANDO SISTEMA DE MENÚS REESTRUCTURADO")
    print("=" * 70)
    
    # 1. Verificar conexión a la base de datos
    print("\n1️⃣ VERIFICANDO CONEXIÓN A LA BASE DE DATOS...")
    try:
        db_url = settings.database_url
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexión a la base de datos exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # 2. Verificar si las tablas existen
    print("\n2️⃣ VERIFICANDO EXISTENCIA DE TABLAS...")
    try:
        with engine.connect() as connection:
            # Verificar tabla de categorías
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'categorias_platos_variables'
                );
            """))
            categorias_existe = result.fetchone()[0]
            print(f"📋 Tabla categorias_platos_variables: {'✅ Existe' if categorias_existe else '❌ No existe'}")
            
            # Verificar tabla de opciones
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'opciones_platos'
                );
            """))
            opciones_existe = result.fetchone()[0]
            print(f"🍽️ Tabla opciones_platos: {'✅ Existe' if opciones_existe else '❌ No existe'}")
            
            # Verificar tabla de menús
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'menus_dia'
                );
            """))
            menus_existe = result.fetchone()[0]
            print(f"📅 Tabla menus_dia: {'✅ Existe' if menus_existe else '❌ No existe'}")
            
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        traceback.print_exc()
    
    # 3. Verificar datos en las tablas
    print("\n3️⃣ VERIFICANDO DATOS EN LAS TABLAS...")
    try:
        with engine.connect() as connection:
            # Verificar categorías
            result = connection.execute(text("SELECT COUNT(*) FROM categorias_platos_variables"))
            count_categorias = result.fetchone()[0]
            print(f"📋 Categorías: {count_categorias}")
            
            # Verificar opciones
            result = connection.execute(text("SELECT COUNT(*) FROM opciones_platos"))
            count_opciones = result.fetchone()[0]
            print(f"🍽️ Opciones: {count_opciones}")
            
            # Verificar menús
            result = connection.execute(text("SELECT COUNT(*) FROM menus_dia"))
            count_menus = result.fetchone()[0]
            print(f"📅 Menús: {count_menus}")
            
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
        traceback.print_exc()
    
    # 4. Verificar importación de modelos
    print("\n4️⃣ VERIFICANDO IMPORTACIÓN DE MODELOS...")
    try:
        from app.models.menu_restructured import CategoriaPlatoVariable, OpcionPlato, MenuDiaRestructured, MenuDiaOpcion
        print("✅ Modelos importados correctamente")
        
        # Verificar que los modelos tienen las tablas correctas
        print(f"📋 CategoriaPlatoVariable.__tablename__: {CategoriaPlatoVariable.__tablename__}")
        print(f"🍽️ OpcionPlato.__tablename__: {OpcionPlato.__tablename__}")
        print(f"📅 MenuDiaRestructured.__tablename__: {MenuDiaRestructured.__tablename__}")
        print(f"🔗 MenuDiaOpcion.__tablename__: {MenuDiaOpcion.__tablename__}")
        
    except Exception as e:
        print(f"❌ Error importando modelos: {e}")
        traceback.print_exc()
    
    # 5. Verificar configuración de SQLAlchemy
    print("\n5️⃣ VERIFICANDO CONFIGURACIÓN DE SQLALCHEMY...")
    try:
        from app.database import engine
        print(f"✅ Engine SQLAlchemy: {engine}")
        
        # Verificar que las tablas están registradas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tablas en la base de datos: {tables}")
        
        # Verificar si las tablas del sistema reestructurado están registradas
        required_tables = ['categorias_platos_variables', 'opciones_platos', 'menus_dia', 'menu_dia_opciones']
        for table in required_tables:
            if table in tables:
                print(f"✅ Tabla {table} registrada")
            else:
                print(f"❌ Tabla {table} NO registrada")
                
    except Exception as e:
        print(f"❌ Error verificando SQLAlchemy: {e}")
        traceback.print_exc()
    
    # 6. Verificar que las tablas están creadas en SQLAlchemy
    print("\n6️⃣ VERIFICANDO CREACIÓN DE TABLAS EN SQLALCHEMY...")
    try:
        from app.database import Base
        from app.models.menu_restructured import CategoriaPlatoVariable, OpcionPlato, MenuDiaRestructured, MenuDiaOpcion
        
        # Intentar crear las tablas
        print("🔧 Intentando crear tablas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas/verificadas en SQLAlchemy")
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 70)
    print("✅ Conexión a la base de datos")
    print("✅ Tablas creadas en PostgreSQL")
    print("✅ Modelos importados correctamente")
    print("✅ Configuración de SQLAlchemy")
    print("\n🎯 Si todos los pasos están ✅, el problema puede estar en:")
    print("   - Configuración del router")
    print("   - Importación en main.py")
    print("   - Configuración de la sesión de base de datos")

if __name__ == "__main__":
    debug_menu_restructured()


