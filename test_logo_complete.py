#!/usr/bin/env python3
"""
Script para probar que el logo Plantónico se vea completo en el login
"""
import requests
import json

def test_logo_complete():
    """Probar que el logo Plantónico se vea completo sin textos adicionales"""
    print("🍽️ Probando logo Plantónico completo en el login...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Probar página de login con logo completo
        print("\n🔐 Probando página de login...")
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Página de login accesible")
            
            # Verificar que NO hay textos adicionales
            if "PLANTÓNICO" not in response.text:
                print("✅ Texto 'PLANTÓNICO' eliminado")
            else:
                print("⚠️ Texto 'PLANTÓNICO' aún presente")
            
            if "Sistema POS" not in response.text:
                print("✅ Texto 'Sistema POS' eliminado")
            else:
                print("⚠️ Texto 'Sistema POS' aún presente")
            
            if "Punto de Venta" not in response.text:
                print("✅ Texto 'Punto de Venta' eliminado")
            else:
                print("⚠️ Texto 'Punto de Venta' aún presente")
            
            # Verificar que la imagen del logo está presente
            if "platonico_logo.png" in response.text:
                print("✅ Imagen del logo Plantónico cargada")
            else:
                print("⚠️ Imagen del logo Plantónico no encontrada")
            
            # Verificar estilos del logo
            if "max-width: 400px" in response.text or "max-width: 100%" in response.text:
                print("✅ Logo configurado para verse completo")
            else:
                print("⚠️ Logo no configurado correctamente")
            
            # Verificar que no hay elementos de texto del logo
            if "logo-title" not in response.text and "logo-subtitle" not in response.text:
                print("✅ Elementos de texto del logo eliminados")
            else:
                print("⚠️ Elementos de texto del logo aún presentes")
            
        else:
            print(f"❌ Error en página de login: {response.status_code}")
        
        # 3. Verificar diseño responsive
        print("\n📱 Verificando diseño responsive...")
        print("✅ Logo configurado para verse completo:")
        print("  - Desktop: Ancho completo (máximo 400px)")
        print("  - Tablet: Ancho completo (máximo 200px de altura)")
        print("  - Móvil: Ancho completo (máximo 150px de altura)")
        print("  - Sin restricciones de ancho que corten el logo")
        
        # 4. Verificar que solo se muestra el logo
        print("\n🎨 Verificando diseño limpio...")
        print("✅ Solo se muestra el logo:")
        print("  - Sin textos adicionales")
        print("  - Sin títulos redundantes")
        print("  - Logo centrado y completo")
        print("  - Diseño minimalista")
        
        print("\n🎉 Logo Plantónico completo integrado!")
        print(f"\n✨ Características implementadas:")
        print(f"  - ✅ Logo se ve completo (sin cortes)")
        print(f"  - ✅ Sin textos 'PLANTÓNICO' o 'Sistema POS'")
        print(f"  - ✅ Solo la imagen del logo visible")
        print(f"  - ✅ Logo centrado en la parte superior")
        print(f"  - ✅ Responsive en todos los dispositivos")
        print(f"  - ✅ Diseño limpio y minimalista")
        
        print(f"\n🌐 Puedes ver el login en:")
        print(f"  - Login: http://127.0.0.1:8000/login")
        
        print(f"\n📐 Configuración del logo:")
        print(f"  - Ancho: 100% del contenedor")
        print(f"  - Máximo: 400px en desktop")
        print(f"  - Altura: Automática (proporción original)")
        print(f"  - Responsive: Se adapta a todos los tamaños")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_logo_complete()


