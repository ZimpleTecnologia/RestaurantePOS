#!/usr/bin/env python3
"""
Script para limpiar caché y forzar recarga
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def clear_cache():
    """Limpiar archivos de caché"""
    try:
        # Limpiar archivos __pycache__
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    cache_dir = os.path.join(root, dir_name)
                    print(f"Eliminando: {cache_dir}")
                    import shutil
                    shutil.rmtree(cache_dir, ignore_errors=True)
        
        print("✅ Caché limpiado")
        print("🔄 Reinicia el servidor para aplicar cambios")
        
    except Exception as e:
        print(f"❌ Error limpiando caché: {e}")

if __name__ == "__main__":
    clear_cache()

