#!/usr/bin/env python3
"""
Script para corregir índices duplicados en columnas únicas
"""
import os
import re

def fix_unique_indexes():
    """Corregir unique=True, index=True a solo unique=True"""
    
    models_dir = "app/models"
    fixed_files = []
    
    for filename in os.listdir(models_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            filepath = os.path.join(models_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar y reemplazar unique=True, index=True
                original_content = content
                content = re.sub(
                    r'unique=True,\s*index=True',
                    'unique=True',
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
    print("🔧 Corrigiendo índices duplicados en columnas únicas...")
    success = fix_unique_indexes()
    
    if success:
        print("✅ Corrección completada")
    else:
        print("ℹ️ No se encontraron problemas")


