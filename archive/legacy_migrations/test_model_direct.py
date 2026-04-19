#!/usr/bin/env python3
"""
Script para probar el modelo directamente sin el servidor
"""
import sys
import os
from sqlalchemy import create_engine, text
from app.config import settings
from app.models.restaurant_menu import CategoriaMenuRestaurante

def test_model_direct():
    """Probar el modelo directamente"""
    print("🔍 Probando modelo directamente...")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
        engine = create_engine(settings.database_url)
        
        with engine.connect() as conn:
            print("✅ Conexión a la base de datos exitosa")
            
            # Probar consulta directa del modelo
            print("\n📋 Probando consulta del modelo...")
            try:
                from sqlalchemy.orm import sessionmaker
                Session = sessionmaker(bind=engine)
                session = Session()
                
                # Obtener una categoría
                categoria = session.query(CategoriaMenuRestaurante).first()
                if categoria:
                    print("✅ Modelo funcionando")
                    print(f"   - ID: {categoria.id}")
                    print(f"   - Nombre: {categoria.nombre}")
                    print(f"   - is_active: {categoria.is_active}")
                    print(f"   - created_at: {categoria.created_at}")
                else:
                    print("❌ No se encontraron categorías")
                
                session.close()
                
            except Exception as e:
                print(f"❌ Error con el modelo: {e}")
                print(f"Tipo de error: {type(e).__name__}")
                
                # Verificar la estructura de la tabla
                print("\n🔍 Verificando estructura de la tabla...")
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'categorias_menu'
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                print("Columnas en la tabla:")
                for col in columns:
                    print(f"   - {col[0]} ({col[1]})")
                
                return False
            
            print("\n🎉 Modelo funcionando correctamente")
            return True
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False

if __name__ == "__main__":
    success = test_model_direct()
    if success:
        print("\n✅ El modelo está funcionando correctamente")
        print("💡 El problema puede estar en el servidor que necesita reiniciarse")
    else:
        print("\n❌ Hay problemas con el modelo")


