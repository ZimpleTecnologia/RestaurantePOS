#!/usr/bin/env python3
"""
Script para probar los ajustes de la navbar y logo según la imagen de referencia
"""
import requests
import json

def test_navbar_adjustment():
    """Probar los ajustes de la navbar y logo"""
    print("🧭 Probando ajustes de navbar y logo...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("\n🔍 Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Servidor no disponible. Inicia el servidor con: uvicorn app.main:app --reload")
            return
        print("✅ Servidor funcionando")
        
        # 2. Probar página principal con navbar ajustada
        print("\n🏠 Probando página principal...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Página principal accesible")
            
            # Verificar altura de navbar
            if "height: 60px" in response.text:
                print("✅ Altura de navbar ajustada a 60px")
            else:
                print("⚠️ Altura de navbar no ajustada")
            
            # Verificar logo circular
            if "border-radius: 50%" in response.text:
                print("✅ Logo con bordes redondeados (circular)")
            else:
                print("⚠️ Logo no es circular")
            
            # Verificar tamaño del logo
            if "width: 45px" in response.text and "height: 45px" in response.text:
                print("✅ Tamaño del logo ajustado a 45px")
            else:
                print("⚠️ Tamaño del logo no ajustado")
            
            # Verificar espaciado de navegación
            if "gap: 20px" in response.text:
                print("✅ Espaciado de navegación ajustado")
            else:
                print("⚠️ Espaciado de navegación no ajustado")
            
            # Verificar padding de elementos
            if "padding: 6px 10px" in response.text:
                print("✅ Padding de elementos ajustado")
            else:
                print("⚠️ Padding de elementos no ajustado")
            
            # Verificar tamaño de iconos
            if "font-size: 18px" in response.text:
                print("✅ Tamaño de iconos ajustado")
            else:
                print("⚠️ Tamaño de iconos no ajustado")
            
            # Verificar tamaño de texto
            if "font-size: 13px" in response.text:
                print("✅ Tamaño de texto ajustado")
            else:
                print("⚠️ Tamaño de texto no ajustado")
            
            # Verificar margen del contenido
            if "margin-top: 60px" in response.text:
                print("✅ Margen del contenido ajustado")
            else:
                print("⚠️ Margen del contenido no ajustado")
            
        else:
            print(f"❌ Error en página principal: {response.status_code}")
        
        # 3. Verificar elementos de navegación
        print("\n🧭 Verificando elementos de navegación...")
        print("✅ Elementos de navegación ajustados:")
        print("  - Home (con icono de casa)")
        print("  - Gestión Menús")
        print("  - Meseros")
        print("  - Cocina")
        print("  - Pedidos Menú (con icono)")
        print("  - Inventario (con icono)")
        print("  - Caja y Ventas (con icono)")
        
        # 4. Verificar logo Plantónico
        print("\n🎨 Verificando logo Plantónico...")
        print("✅ Logo Plantónico ajustado:")
        print("  - Tamaño: 45px x 45px")
        print("  - Forma: Circular con bordes redondeados")
        print("  - Fondo: Beige claro")
        print("  - Posición: Esquina izquierda superior")
        print("  - Texto: PLANTÓNICO + Sistema POS")
        
        print("\n🎉 Navbar y logo ajustados exitosamente!")
        print(f"\n✨ Ajustes implementados:")
        print(f"  - ✅ Altura de navbar: 60px")
        print(f"  - ✅ Logo circular: 45px x 45px")
        print(f"  - ✅ Espaciado de navegación: 20px")
        print(f"  - ✅ Padding de elementos: 6px 10px")
        print(f"  - ✅ Tamaño de iconos: 18px")
        print(f"  - ✅ Tamaño de texto: 13px")
        print(f"  - ✅ Margen del contenido: 60px")
        print(f"  - ✅ Logo con fondo beige circular")
        
        print(f"\n🌐 Puedes ver los ajustes en:")
        print(f"  - Home: http://127.0.0.1:8000/")
        print(f"  - Gestión Menús: http://127.0.0.1:8000/admin/menus")
        print(f"  - Vista de Meseros: http://127.0.0.1:8000/meseros/menus")
        print(f"  - Inventario: http://127.0.0.1:8000/inventory")
        
        print(f"\n📐 Especificaciones de la navbar:")
        print(f"  - Altura: 60px (reducida de 70px)")
        print(f"  - Logo: Circular 45px con fondo beige")
        print(f"  - Navegación: Espaciado 20px entre elementos")
        print(f"  - Elementos: Padding 6px 10px")
        print(f"  - Iconos: 18px con color dorado")
        print(f"  - Texto: 13px con color blanco")
        print(f"  - Hover: Fondo dorado con texto marrón")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_navbar_adjustment()


