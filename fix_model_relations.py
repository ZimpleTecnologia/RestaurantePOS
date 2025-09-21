#!/usr/bin/env python3
"""
Script para corregir las relaciones del modelo MenuDiaRestructured
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database import engine
from app.models.menu_restructured import MenuDiaRestructured, MenuDiaOpcion, OpcionPlato

def fix_model_relations():
    """Corregir las relaciones del modelo"""
    try:
        print("🔧 Corrigiendo relaciones del modelo...")
        
        with engine.connect() as conn:
            # 1. Verificar la estructura de las tablas
            print("\n1. 📋 Verificando estructura de tablas...")
            
            # Verificar menus_dia
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'menus_dia' 
                ORDER BY ordinal_position
            """))
            
            menus_columns = result.fetchall()
            print("   Tabla menus_dia:")
            for col in menus_columns:
                print(f"   - {col[0]} ({col[1]}) - Nullable: {col[2]}")
            
            # Verificar menu_dia_opciones
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'menu_dia_opciones' 
                ORDER BY ordinal_position
            """))
            
            opciones_columns = result.fetchall()
            print("   Tabla menu_dia_opciones:")
            for col in opciones_columns:
                print(f"   - {col[0]} ({col[1]}) - Nullable: {col[2]}")
            
            # 2. Verificar claves foráneas
            print("\n2. 🔑 Verificando claves foráneas...")
            result = conn.execute(text("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name = 'menu_dia_opciones'
                ORDER BY kcu.column_name
            """))
            
            fks = result.fetchall()
            print("   Claves foráneas en menu_dia_opciones:")
            for fk in fks:
                print(f"   - {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]} ({fk[0]})")
            
            # 3. Verificar datos existentes
            print("\n3. 📊 Verificando datos existentes...")
            
            # Contar menús
            result = conn.execute(text("SELECT COUNT(*) FROM menus_dia"))
            menu_count = result.scalar()
            print(f"   Menús existentes: {menu_count}")
            
            # Contar opciones
            result = conn.execute(text("SELECT COUNT(*) FROM menu_dia_opciones"))
            opciones_count = result.scalar()
            print(f"   Opciones existentes: {opciones_count}")
            
            # 4. Verificar relaciones de datos
            print("\n4. 🔗 Verificando relaciones de datos...")
            result = conn.execute(text("""
                SELECT 
                    md.id as menu_id,
                    md.nombre as menu_nombre,
                    COUNT(mdo.id) as opciones_count
                FROM menus_dia md
                LEFT JOIN menu_dia_opciones mdo ON md.id = mdo.menu_dia_id
                GROUP BY md.id, md.nombre
                ORDER BY md.id
            """))
            
            relaciones = result.fetchall()
            print("   Relaciones encontradas:")
            for rel in relaciones:
                print(f"   - Menú {rel[0]} ({rel[1]}) tiene {rel[2]} opciones")
            
            # 5. Probar consulta directa
            print("\n5. 🧪 Probando consulta directa...")
            try:
                result = conn.execute(text("""
                    SELECT md.id, md.nombre, mdo.id as opcion_id, mdo.opcion_id as opcion_ref
                    FROM menus_dia md
                    JOIN menu_dia_opciones mdo ON md.id = mdo.menu_dia_id
                    LIMIT 3
                """))
                
                datos = result.fetchall()
                print("   Datos de relación:")
                for dato in datos:
                    print(f"   - Menú {dato[0]} ({dato[1]}) -> Opción {dato[2]} (ref: {dato[3]})")
                
            except Exception as e:
                print(f"   ❌ Error en consulta directa: {str(e)}")
            
            print("\n🎉 Verificación de relaciones completada!")
            
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False
    
    return True

def test_model_creation():
    """Probar la creación de modelos directamente"""
    try:
        print("\n🔧 Probando creación de modelos...")
        
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Probar crear un menú simple
        print("   Creando menú de prueba...")
        nuevo_menu = MenuDiaRestructured(
            fecha='2025-09-26',
            nombre='Test Menu Model',
            descripcion='Test desde modelo',
            precio=14000,
            estado='ACTIVE'
        )
        
        session.add(nuevo_menu)
        session.commit()
        session.refresh(nuevo_menu)
        
        print(f"   ✅ Menú creado: ID {nuevo_menu.id}")
        
        # Probar crear una opción
        print("   Creando opción de prueba...")
        nueva_opcion = MenuDiaOpcion(
            menu_dia_id=nuevo_menu.id,
            opcion_id=1,  # Asumiendo que existe
            disponible=True
        )
        
        session.add(nueva_opcion)
        session.commit()
        session.refresh(nueva_opcion)
        
        print(f"   ✅ Opción creada: ID {nueva_opcion.id}")
        
        # Limpiar datos de prueba
        session.delete(nueva_opcion)
        session.delete(nuevo_menu)
        session.commit()
        
        print("   🧹 Datos de prueba limpiados")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error en creación de modelos: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🔧 Script de Corrección de Relaciones del Modelo")
    print("=" * 60)
    
    # Verificar relaciones
    relations_success = fix_model_relations()
    
    # Probar creación de modelos
    creation_success = test_model_creation()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print(f"   Verificación de relaciones: {'✅ OK' if relations_success else '❌ ERROR'}")
    print(f"   Creación de modelos: {'✅ OK' if creation_success else '❌ ERROR'}")
    
    if relations_success and creation_success:
        print("\n🎉 Modelo funcionando correctamente!")
        print("   El problema debe estar en el endpoint específico.")
    else:
        print("\n⚠️ Hay problemas con el modelo.")
        print("   Revisa los errores específicos arriba.")
