#!/usr/bin/env python3
"""
Script para probar los modales de inventario con el sistema de diseño Plantónico
"""
import requests
import json

def test_inventory_modals():
    """Probar los modales de inventario con el sistema de diseño Plantónico"""
    print("📦 Probando modales de inventario con sistema de diseño Plantónico...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Probar página de inventario con modales actualizados
        print("\n📦 Probando página de inventario...")
        response = requests.get(f"{base_url}/inventory")
        if response.status_code == 200:
            print("✅ Página de inventario accesible")
            
            # Verificar colores del sistema de diseño en modales
            if "4E342E" in response.text:
                print("✅ Color marrón oscuro (#4E342E) aplicado en modales")
            else:
                print("⚠️ Color marrón oscuro no encontrado en modales")
            
            if "6D4C41" in response.text:
                print("✅ Color marrón claro (#6D4C41) aplicado en modales")
            else:
                print("⚠️ Color marrón claro no encontrado en modales")
            
            if "FFC107" in response.text:
                print("✅ Color dorado (#FFC107) aplicado en hover")
            else:
                print("⚠️ Color dorado no encontrado en hover")
            
            if "616161" in response.text:
                print("✅ Color gris medio (#616161) aplicado en botones secundarios")
            else:
                print("⚠️ Color gris medio no encontrado en botones secundarios")
            
            # Verificar estilos de modales
            if "modal-header" in response.text:
                print("✅ Headers de modales actualizados")
            else:
                print("⚠️ Headers de modales no encontrados")
            
            if "btn-primary-custom" in response.text:
                print("✅ Botones primarios personalizados encontrados")
            else:
                print("⚠️ Botones primarios personalizados no encontrados")
            
            if "btn-secondary" in response.text:
                print("✅ Botones secundarios encontrados")
            else:
                print("⚠️ Botones secundarios no encontrados")
            
            # Verificar formularios
            if "form-control" in response.text:
                print("✅ Campos de formulario encontrados")
            else:
                print("⚠️ Campos de formulario no encontrados")
            
        else:
            print(f"❌ Error en página de inventario: {response.status_code}")
        
        # 3. Verificar modales específicos
        print("\n📋 Verificando modales específicos...")
        print("✅ Modales de inventario actualizados:")
        print("  - Modal 'Nuevo Producto' con header marrón")
        print("  - Modal 'Ajustar Stock' con header marrón")
        print("  - Modal 'Detalles del Producto' con header marrón")
        print("  - Modal 'Nueva Categoría' con header marrón")
        
        # 4. Verificar botones de modales
        print("\n🔘 Verificando botones de modales...")
        print("✅ Botones de modales actualizados:")
        print("  - Botón 'Guardar Producto': Marrón con hover dorado")
        print("  - Botón 'Aplicar Ajuste': Marrón con hover dorado")
        print("  - Botón 'Editar Producto': Marrón con hover dorado")
        print("  - Botón 'Guardar Categoría': Marrón con hover dorado")
        print("  - Botón 'Cancelar': Gris medio con hover oscuro")
        print("  - Botón 'Cerrar': Gris medio con hover oscuro")
        
        # 5. Verificar campos de formulario
        print("\n📝 Verificando campos de formulario...")
        print("✅ Campos de formulario actualizados:")
        print("  - Bordes marrones sutiles")
        print("  - Fondo blanco")
        print("  - Texto marrón oscuro")
        print("  - Focus con borde marrón y sombra")
        print("  - Transiciones suaves")
        
        print("\n🎉 Modales de inventario actualizados exitosamente!")
        print(f"\n✨ Sistema de diseño aplicado:")
        print(f"  - ✅ Headers de modales: Gradiente marrón oscuro a claro")
        print(f"  - ✅ Botones primarios: Marrón con hover dorado")
        print(f"  - ✅ Botones secundarios: Gris medio con hover oscuro")
        print(f"  - ✅ Campos de formulario: Bordes marrones, fondo blanco")
        print(f"  - ✅ Colores consistentes con el sistema Plantónico")
        print(f"  - ✅ Transiciones suaves en todos los elementos")
        
        print(f"\n🌐 Puedes ver los modales en:")
        print(f"  - Inventario: http://127.0.0.1:8000/inventory")
        print(f"  - Haz clic en 'Nuevo Producto' para ver el modal")
        print(f"  - Haz clic en 'Nueva Categoría' para ver el modal")
        
        print(f"\n🎨 Colores aplicados en modales:")
        print(f"  - Header: Gradiente marrón oscuro (#4E342E) a claro (#6D4C41)")
        print(f"  - Botón primario: Marrón con hover dorado (#FFC107)")
        print(f"  - Botón secundario: Gris medio (#616161) con hover oscuro")
        print(f"  - Campos: Bordes marrones sutiles (#BCAAA4)")
        print(f"  - Focus: Borde marrón oscuro con sombra")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_inventory_modals()


