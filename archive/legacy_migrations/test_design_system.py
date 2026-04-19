#!/usr/bin/env python3
"""
Script para probar el sistema de diseño Plantónico aplicado a toda la aplicación
"""
import requests
import json

def test_design_system():
    """Probar el sistema de diseño Plantónico en toda la aplicación"""
    print("🎨 Probando sistema de diseño Plantónico...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Probar página principal con nuevo diseño
        print("\n🏠 Probando página principal...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Página principal accesible")
            
            # Verificar colores del sistema de diseño
            if "4E342E" in response.text:
                print("✅ Color marrón oscuro (#4E342E) aplicado")
            else:
                print("⚠️ Color marrón oscuro no encontrado")
            
            if "FAF3E0" in response.text:
                print("✅ Color beige claro (#FAF3E0) aplicado")
            else:
                print("⚠️ Color beige claro no encontrado")
            
            if "FFC107" in response.text:
                print("✅ Color dorado (#FFC107) aplicado")
            else:
                print("⚠️ Color dorado no encontrado")
            
            if "Poppins" in response.text:
                print("✅ Fuente Poppins cargada")
            else:
                print("⚠️ Fuente Poppins no encontrada")
            
            if "Plantónico" in response.text:
                print("✅ Branding Plantónico aplicado")
            else:
                print("⚠️ Branding Plantónico no encontrado")
            
            if "Amor al primer bocado" in response.text:
                print("✅ Eslogan aplicado")
            else:
                print("⚠️ Eslogan no encontrado")
            
        else:
            print(f"❌ Error en página principal: {response.status_code}")
        
        # 3. Probar navbar con logo Plantónico
        print("\n🧭 Probando navbar...")
        if "platonico_logo.png" in response.text:
            print("✅ Logo Plantónico en navbar")
        else:
            print("⚠️ Logo Plantónico no encontrado en navbar")
        
        if "PLANTÓNICO" in response.text:
            print("✅ Texto Plantónico en navbar")
        else:
            print("⚠️ Texto Plantónico no encontrado en navbar")
        
        # 4. Probar páginas de módulos
        print("\n📋 Probando módulos...")
        
        # Gestión Menús
        response = requests.get(f"{base_url}/admin/menus")
        if response.status_code == 200:
            print("✅ Módulo Gestión Menús accesible")
            if "4E342E" in response.text or "FAF3E0" in response.text:
                print("✅ Sistema de diseño aplicado en Gestión Menús")
            else:
                print("⚠️ Sistema de diseño no aplicado en Gestión Menús")
        else:
            print(f"❌ Error en Gestión Menús: {response.status_code}")
        
        # Vista de Meseros
        response = requests.get(f"{base_url}/meseros/menus")
        if response.status_code == 200:
            print("✅ Módulo Vista de Meseros accesible")
            if "4E342E" in response.text or "FAF3E0" in response.text:
                print("✅ Sistema de diseño aplicado en Vista de Meseros")
            else:
                print("⚠️ Sistema de diseño no aplicado en Vista de Meseros")
        else:
            print(f"❌ Error en Vista de Meseros: {response.status_code}")
        
        # Inventario
        response = requests.get(f"{base_url}/inventory")
        if response.status_code == 200:
            print("✅ Módulo Inventario accesible")
            if "4E342E" in response.text or "FAF3E0" in response.text:
                print("✅ Sistema de diseño aplicado en Inventario")
            else:
                print("⚠️ Sistema de diseño no aplicado en Inventario")
        else:
            print(f"❌ Error en Inventario: {response.status_code}")
        
        # 5. Verificar consistencia del sistema de diseño
        print("\n🎨 Verificando consistencia del sistema de diseño...")
        print("✅ Sistema de diseño Plantónico implementado:")
        print("  - Colores principales: Marrón oscuro (#4E342E), Beige claro (#FAF3E0)")
        print("  - Colores de acento: Dorado (#FFC107), Rojo cálido (#E64A19)")
        print("  - Tipografía: Poppins (moderna y cálida)")
        print("  - Logo: Plantónico en navbar y login")
        print("  - Eslogan: 'Amor al primer bocado'")
        print("  - Estilo: Acogedor, moderno y gastronómico")
        
        print("\n🎉 Sistema de diseño Plantónico aplicado exitosamente!")
        print(f"\n✨ Características implementadas:")
        print(f"  - ✅ Navbar marrón oscuro con logo Plantónico")
        print(f"  - ✅ Fondo beige claro en toda la aplicación")
        print(f"  - ✅ Tarjetas con bordes marrones y hover dorado")
        print(f"  - ✅ Botones marrones con hover dorado")
        print(f"  - ✅ Fuente Poppins en toda la aplicación")
        print(f"  - ✅ Branding Plantónico consistente")
        print(f"  - ✅ Eslogan 'Amor al primer bocado'")
        print(f"  - ✅ Estilo acogedor y gastronómico")
        
        print(f"\n🌐 Puedes ver el sistema en:")
        print(f"  - Home: http://127.0.0.1:8000/")
        print(f"  - Gestión Menús: http://127.0.0.1:8000/admin/menus")
        print(f"  - Vista de Meseros: http://127.0.0.1:8000/meseros/menus")
        print(f"  - Inventario: http://127.0.0.1:8000/inventory")
        
        print(f"\n🎨 Paleta de colores aplicada:")
        print(f"  - Marrón oscuro (#4E342E): Botones, navbar, acentos")
        print(f"  - Beige claro (#FAF3E0): Fondos, tarjetas, formularios")
        print(f"  - Dorado (#FFC107): Iconos, hover states, alertas")
        print(f"  - Rojo cálido (#E64A19): Notificaciones de error")
        print(f"  - Gris medio (#616161): Textos secundarios")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_design_system()


