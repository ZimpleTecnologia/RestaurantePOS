#!/usr/bin/env python3
"""
Script para corregir índices duplicados en modelos SQLAlchemy
"""
import os
import re

def fix_duplicate_indexes():
    """Corregir primary_key=True, index=True a primary_key=True"""
    
    models_dir = "app/models"
    fixed_files = []
    
    for filename in os.listdir(models_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(models_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar y reemplazar primary_key=True, index=True
                original_content = content
                content = re.sub(
                    r'primary_key=True,\s*index=True',
                    'primary_key=True',
                    content
                )
                
                # Si hubo cambios, escribir el archivo
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_files.append(filename)
                    print(f"✅ Corregido: {filename}")
                
            except Exception as e:
                print(f"❌ Error procesando {filename}: {e}")
    
    print(f"\n📊 Archivos corregidos: {len(fixed_files)}")
    for file in fixed_files:
        print(f"   - {file}")
    
    return len(fixed_files) > 0

if __name__ == "__main__":
    print("🔧 Corrigiendo índices duplicados en modelos...")
    success = fix_duplicate_indexes()
    
    if success:
        print("✅ Corrección completada")
    else:
        print("ℹ️ No se encontraron problemas")


