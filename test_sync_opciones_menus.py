#!/usr/bin/env python3
"""
Script de prueba para verificar la sincronización automática entre opciones y menús
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

def get_opciones():
    """Obtener lista de opciones disponibles"""
    print_header("2. OBTENER OPCIONES DISPONIBLES")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/menu-restructured/opciones/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                opciones = data.get('opciones', [])
                print_success(f"Se obtuvieron {len(opciones)} opciones")
                
                # Mostrar opciones que están en menús
                opciones_en_menus = [op for op in opciones if op.get('activo', False)]
                print_info(f"Opciones activas: {len(opciones_en_menus)}")
                
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

def test_sync_status(opcion_id):
    """Verificar estado de sincronización de una opción"""
    print_header(f"3. VERIFICAR SINCRONIZACIÓN - OPCIÓN ID {opcion_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/menu-restructured/opciones/{opcion_id}/sync-status")
        
        if response.status_code == 200:
            data = response.json()
            opcion = data.get('opcion', {})
            sync = data.get('sincronizacion', {})
            menus = data.get('menus', [])
            
            print_success(f"Estado de sincronización obtenido")
            print_info(f"Opción: {opcion.get('nombre')} (ID: {opcion.get('id')})")
            print_info(f"Estado: {'Activa' if opcion.get('activo') else 'Inactiva'}")
            print_info(f"Sincronización: {sync.get('estado')}")
            print_info(f"Total menús: {sync.get('total_menus')}")
            print_info(f"Disponibles: {sync.get('menus_disponibles')}")
            print_info(f"No disponibles: {sync.get('menus_no_disponibles')}")
            
            if menus:
                print_info("\nDetalles de menús:")
                for menu in menus:
                    estado = "✅ Disponible" if menu.get('disponible') else "❌ No disponible"
                    deberia = "✅ Debería estar" if menu.get('deberia_estar_disponible') else "❌ No debería estar"
                    print(f"   - Menú {menu.get('menu_id')} ({menu.get('fecha')}): {estado} | {deberia}")
            
            return data
        else:
            print_error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_toggle_opcion(opcion_id):
    """Probar toggle de una opción"""
    print_header(f"4. PROBAR TOGGLE - OPCIÓN ID {opcion_id}")
    
    print_warning("Esta prueba cambiará el estado de la opción")
    respuesta = input(f"\n¿Continuar con el toggle de la opción ID {opcion_id}? (s/N): ")
    if respuesta.lower() != 's':
        print_info("Prueba omitida por el usuario")
        return None
    
    try:
        response = requests.patch(f"{BASE_URL}/api/v1/menu-restructured/opciones/{opcion_id}/toggle-status")
        
        if response.status_code == 200:
            data = response.json()
            opcion = data.get('opcion', {})
            menus_updated = data.get('menus_updated', 0)
            
            print_success(f"Toggle exitoso")
            print_info(f"Mensaje: {data.get('message')}")
            print_info(f"Menús actualizados: {menus_updated}")
            print_info(f"Estado actual: {'Activa' if opcion.get('activo') else 'Inactiva'}")
            
            return data
        else:
            print_error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_delete_opcion(opcion_id):
    """Probar eliminación/desactivación de una opción"""
    print_header(f"5. PROBAR ELIMINACIÓN - OPCIÓN ID {opcion_id}")
    
    print_warning("Esta prueba intentará eliminar/desactivar la opción")
    respuesta = input(f"\n¿Continuar con la eliminación de la opción ID {opcion_id}? (s/N): ")
    if respuesta.lower() != 's':
        print_info("Prueba omitida por el usuario")
        return None
    
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/menu-restructured/opciones/{opcion_id}")
        
        if response.status_code == 200:
            data = response.json()
            action = data.get('action', 'unknown')
            menus_updated = data.get('menus_updated', 0)
            
            print_success(f"Operación exitosa")
            print_info(f"Acción: {action}")
            print_info(f"Mensaje: {data.get('message')}")
            print_info(f"Menús actualizados: {menus_updated}")
            
            if action == 'deleted':
                print_success("✨ Opción eliminada permanentemente")
            elif action == 'deactivated':
                print_warning("⚠️ Opción desactivada y removida de menús")
            elif action == 'already_inactive':
                print_info("ℹ️ Opción ya estaba desactivada")
            
            return data
        else:
            print_error(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║        PRUEBA DE SINCRONIZACIÓN OPCIONES-MENÚS                     ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # Verificar conexión
    if not test_connection():
        return
    
    # Obtener opciones
    opciones = get_opciones()
    if not opciones:
        print_error("No se pudieron obtener opciones")
        return
    
    # Buscar una opción para probar
    opcion_para_probar = None
    for opcion in opciones:
        if opcion.get('activo', False):
            opcion_para_probar = opcion
            break
    
    if not opcion_para_probar:
        print_warning("No se encontraron opciones activas para probar")
        return
    
    opcion_id = opcion_para_probar.get('id')
    print_info(f"Opción seleccionada para pruebas: {opcion_para_probar.get('nombre')} (ID: {opcion_id})")
    
    # Verificar estado inicial
    print("\n" + "="*50)
    print("ESTADO INICIAL")
    print("="*50)
    test_sync_status(opcion_id)
    
    # Probar toggle
    print("\n" + "="*50)
    print("PROBANDO TOGGLE")
    print("="*50)
    test_toggle_opcion(opcion_id)
    
    # Verificar estado después del toggle
    print("\n" + "="*50)
    print("ESTADO DESPUÉS DEL TOGGLE")
    print("="*50)
    test_sync_status(opcion_id)
    
    # Probar eliminación
    print("\n" + "="*50)
    print("PROBANDO ELIMINACIÓN")
    print("="*50)
    test_delete_opcion(opcion_id)
    
    # Verificar estado final
    print("\n" + "="*50)
    print("ESTADO FINAL")
    print("="*50)
    test_sync_status(opcion_id)
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}Pruebas completadas{Colors.RESET}\n")

if __name__ == "__main__":
    main()


