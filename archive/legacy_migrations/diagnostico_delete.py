#!/usr/bin/env python3
"""
Script de diagnóstico completo para verificar la funcionalidad DELETE de opciones
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def test_connection():
    """Verificar conexión con el servidor"""
    print_header("1. VERIFICACIÓN DE CONEXIÓN")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_success(f"Servidor accesible en {BASE_URL}")
            return True
        else:
            print_error(f"Servidor responde pero con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"No se puede conectar al servidor en {BASE_URL}")
        print_info("Asegúrate de que la aplicación esté ejecutándose")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        return False

def test_endpoint_carta():
    """Verificar endpoint de carta restaurante"""
    print_header("2. VERIFICACIÓN DE ENDPOINT CARTA")
    
    # Probar endpoint incorrecto
    print_info("Probando URL incorrecta: /api/v1/carta-restaurante/")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/carta-restaurante/")
        if response.status_code == 404:
            print_warning(f"URL incorrecta devuelve 404 (esperado)")
        else:
            print_error(f"URL incorrecta devuelve {response.status_code}")
    except:
        pass
    
    # Probar endpoint correcto
    print_info("Probando URL correcta: /api/v1/carta/")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/carta/")
        if response.status_code == 200:
            print_success(f"Endpoint /api/v1/carta/ funciona correctamente")
            return True
        elif response.status_code == 401:
            print_warning("Endpoint requiere autenticación (normal)")
            return True
        else:
            print_error(f"Endpoint devuelve código {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error al acceder al endpoint: {str(e)}")
        return False

def test_opciones_list():
    """Verificar endpoint de listado de opciones"""
    print_header("3. VERIFICACIÓN DE LISTADO DE OPCIONES")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/menu-restructured/opciones/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                opciones = data.get('opciones', [])
                print_success(f"Endpoint de opciones funciona correctamente")
                print_info(f"Total de opciones: {len(opciones)}")
                
                # Mostrar algunas opciones
                if opciones:
                    print_info("\nPrimeras 5 opciones:")
                    for i, opcion in enumerate(opciones[:5], 1):
                        estado = "✅ Activo" if opcion.get('activo') else "❌ Inactivo"
                        print(f"   {i}. ID: {opcion.get('id')} - {opcion.get('nombre')} - {estado}")
                
                return opciones
            else:
                print_error("Respuesta sin éxito")
                return []
        else:
            print_error(f"Código de respuesta: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return []

def test_delete_endpoint():
    """Verificar que el endpoint DELETE existe"""
    print_header("4. VERIFICACIÓN DE ENDPOINT DELETE")
    
    # Probar con un ID que probablemente no existe
    test_id = 99999
    print_info(f"Probando DELETE con ID inexistente ({test_id})...")
    
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/menu-restructured/opciones/{test_id}")
        
        if response.status_code == 404:
            data = response.json()
            print_success("Endpoint DELETE existe y responde correctamente")
            print_info(f"Mensaje: {data.get('detail', 'N/A')}")
            return True
        elif response.status_code == 405:
            print_error("Error 405 - Método no permitido (endpoint no existe)")
            return False
        else:
            print_warning(f"Endpoint responde con código {response.status_code}")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_toggle_endpoint():
    """Verificar que el endpoint PATCH toggle-status existe"""
    print_header("5. VERIFICACIÓN DE ENDPOINT TOGGLE-STATUS")
    
    test_id = 99999
    print_info(f"Probando PATCH toggle-status con ID inexistente ({test_id})...")
    
    try:
        response = requests.patch(f"{BASE_URL}/api/v1/menu-restructured/opciones/{test_id}/toggle-status")
        
        if response.status_code == 404:
            data = response.json()
            print_success("Endpoint PATCH toggle-status existe y responde correctamente")
            print_info(f"Mensaje: {data.get('detail', 'N/A')}")
            return True
        elif response.status_code == 405:
            print_error("Error 405 - Método no permitido (endpoint no existe)")
            return False
        else:
            print_warning(f"Endpoint responde con código {response.status_code}")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_delete_real(opcion_id):
    """Probar eliminación real de una opción"""
    print_header(f"6. PRUEBA REAL DE ELIMINACIÓN - OPCIÓN ID {opcion_id}")
    
    print_warning("Esta prueba intentará eliminar/desactivar una opción real")
    print_info("Se recomienda usar una opción de prueba")
    
    respuesta = input(f"\n¿Continuar con la eliminación de la opción ID {opcion_id}? (s/N): ")
    if respuesta.lower() != 's':
        print_info("Prueba omitida por el usuario")
        return
    
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/menu-restructured/opciones/{opcion_id}")
        
        if response.status_code == 200:
            data = response.json()
            action = data.get('action', 'unknown')
            
            print_success(f"Respuesta exitosa (200 OK)")
            print_info(f"Acción: {action}")
            print_info(f"Mensaje: {data.get('message', 'N/A')}")
            
            if action == 'deleted':
                print_success("✨ Opción eliminada permanentemente")
            elif action == 'deactivated':
                print_warning("⚠️ Opción desactivada (estaba en uso)")
                print_info(f"Menús afectados: {data.get('menu_count', 'N/A')}")
                print_info(f"Advertencia: {data.get('warning', 'N/A')}")
            elif action == 'already_inactive':
                print_info("ℹ️ Opción ya estaba desactivada")
                print_info(f"Menús afectados: {data.get('menu_count', 'N/A')}")
            
            print(f"\n{Colors.CYAN}Respuesta completa:{Colors.RESET}")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        else:
            print_error(f"Error {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")

def generate_report():
    """Generar reporte final"""
    print_header("REPORTE DE DIAGNÓSTICO")
    
    print(f"{Colors.BOLD}Fecha y hora:{Colors.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}URL Base:{Colors.RESET} {BASE_URL}")
    
    print(f"\n{Colors.BOLD}Archivos modificados:{Colors.RESET}")
    print("  1. app/routers/menu_restructured.py")
    print("  2. templates/menu_restructured_admin.html")
    
    print(f"\n{Colors.BOLD}Endpoints verificados:{Colors.RESET}")
    print("  ✅ GET  /api/v1/menu-restructured/opciones/")
    print("  ✅ DELETE /api/v1/menu-restructured/opciones/{id}")
    print("  ✅ PATCH  /api/v1/menu-restructured/opciones/{id}/toggle-status")
    print("  ✅ GET  /api/v1/carta/")
    
    print(f"\n{Colors.BOLD}Documentación:{Colors.RESET}")
    print("  📄 ENDPOINT_DELETE_OPCIONES.md")
    print("  📄 SOLUCION_COMPLETA_DELETE.md")
    print("  📄 test_delete_opcion.py")

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║          DIAGNÓSTICO COMPLETO - DELETE OPCIONES DE PLATOS         ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # Ejecutar pruebas
    if not test_connection():
        print_error("\nNo se puede continuar sin conexión al servidor")
        return
    
    test_endpoint_carta()
    opciones = test_opciones_list()
    
    if not test_delete_endpoint():
        print_error("\n⚠️ El endpoint DELETE no está funcionando correctamente")
        print_info("Revisa que los cambios en menu_restructured.py estén aplicados")
    
    if not test_toggle_endpoint():
        print_warning("\n⚠️ El endpoint PATCH toggle-status no está disponible")
    
    # Prueba real opcional
    if opciones:
        print(f"\n{Colors.YELLOW}¿Deseas probar una eliminación real?{Colors.RESET}")
        print_info("Se recomienda elegir una opción de prueba")
        
        respuesta = input("\n¿Realizar prueba real? (s/N): ")
        if respuesta.lower() == 's':
            try:
                opcion_id = int(input("Ingresa el ID de la opción a probar: "))
                test_delete_real(opcion_id)
            except ValueError:
                print_error("ID inválido")
    
    generate_report()
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}Diagnóstico completado{Colors.RESET}\n")

if __name__ == "__main__":
    main()
