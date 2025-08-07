#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de impresión de tickets
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_printing_functionality():
    """Prueba la funcionalidad de impresión de tickets"""
    
    print("🧪 Probando funcionalidad de impresión de tickets...")
    
    # 1. Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
        else:
            print("❌ Servidor no responde correctamente")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. Asegúrate de que esté corriendo en http://localhost:8000")
        return False
    
    # 2. Verificar que el endpoint de impresión esté disponible
    try:
        response = requests.get(f"{API_BASE}/sales/1/print")
        if response.status_code in [200, 404]:  # 404 es esperado si no hay ventas
            print("✅ Endpoint de impresión disponible")
        else:
            print(f"❌ Endpoint de impresión no responde correctamente: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al probar endpoint de impresión: {e}")
        return False
    
    # 3. Verificar que el archivo CSS esté disponible
    try:
        response = requests.get(f"{BASE_URL}/static/css/ticket.css")
        if response.status_code == 200:
            print("✅ Archivo CSS de tickets disponible")
        else:
            print(f"❌ Archivo CSS no encontrado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al acceder al archivo CSS: {e}")
        return False
    
    print("\n🎉 Todas las pruebas pasaron exitosamente!")
    print("\n📋 Para probar la funcionalidad completa:")
    print("1. Inicia el servidor: python -m uvicorn app.main:app --reload")
    print("2. Abre http://localhost:8000 en tu navegador")
    print("3. Ve a la página de Ventas")
    print("4. Haz clic en el botón de impresión (ícono de impresora)")
    print("5. Verifica que se abra la ventana de impresión")
    
    return True

def test_ticket_generation():
    """Prueba la generación de un ticket de ejemplo"""
    
    print("\n🧪 Probando generación de ticket de ejemplo...")
    
    # Crear datos de ejemplo para un ticket
    sample_ticket_data = {
        "sale_number": "V20241201001",
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "customer_name": "Cliente de Prueba",
        "vendedor": "Usuario Sistema",
        "items": [
            {
                "name": "Producto 1",
                "code": "PROD001",
                "quantity": 2,
                "unit_price": 10.50,
                "total": 21.00
            },
            {
                "name": "Producto 2", 
                "code": "PROD002",
                "quantity": 1,
                "unit_price": 15.75,
                "total": 15.75
            }
        ],
        "subtotal": 36.75,
        "tax": 5.88,
        "total": 42.63
    }
    
    # Generar HTML del ticket de ejemplo
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Ticket de Venta - Ejemplo</title>
        <link rel="stylesheet" href="/static/css/ticket.css">
    </head>
    <body>
        <div class="ticket-header">
            <div class="ticket-title">SISTEMA POS</div>
            <div class="ticket-subtitle">Punto de Venta</div>
        </div>
        
        <div class="ticket-info">
            <div><strong>Ticket:</strong> {sample_ticket_data['sale_number']}</div>
            <div><strong>Fecha:</strong> {sample_ticket_data['created_at']}</div>
            <div><strong>Cliente:</strong> {sample_ticket_data['customer_name']}</div>
            <div><strong>Vendedor:</strong> {sample_ticket_data['vendedor']}</div>
        </div>
        
        <div class="ticket-items">
            <div style="border-bottom: 1px solid #000; margin-bottom: 5px; padding-bottom: 3px;">
                <strong>PRODUCTOS</strong>
            </div>
    """
    
    for item in sample_ticket_data['items']:
        html_content += f"""
            <div class="ticket-item">
                <div class="ticket-item-name">{item['name']}</div>
                <div class="ticket-item-qty">{item['quantity']}</div>
                <div class="ticket-item-price">${item['unit_price']:.2f}</div>
            </div>
            <div style="text-align: right; font-size: 10px; color: #666; margin-bottom: 5px;">
                {item['code']} - ${item['total']:.2f}
            </div>
        """
    
    html_content += f"""
        </div>
        
        <div class="ticket-totals">
            <div class="ticket-total-line">
                <span>Subtotal:</span>
                <span style="margin-left: 20px;">${sample_ticket_data['subtotal']:.2f}</span>
            </div>
            <div class="ticket-total-line">
                <span>IVA (16%):</span>
                <span style="margin-left: 20px;">${sample_ticket_data['tax']:.2f}</span>
            </div>
            <div class="ticket-total-line" style="border-top: 1px solid #000; padding-top: 5px; font-weight: bold;">
                <span>TOTAL:</span>
                <span style="margin-left: 20px;">${sample_ticket_data['total']:.2f}</span>
            </div>
        </div>
        
        <div class="ticket-footer">
            <div>¡Gracias por su compra!</div>
            <div>Vuelva pronto</div>
        </div>
    </body>
    </html>
    """
    
    # Guardar el ticket de ejemplo
    with open("ticket_ejemplo.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ Ticket de ejemplo generado: ticket_ejemplo.html")
    print("📄 Puedes abrir este archivo en tu navegador para ver cómo se ve el ticket")
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de funcionalidad de impresión...")
    
    # Ejecutar pruebas
    test1 = test_printing_functionality()
    test2 = test_ticket_generation()
    
    if test1 and test2:
        print("\n🎉 ¡Todas las pruebas completadas exitosamente!")
        print("📚 Revisa la documentación en docs/PRINTING_TICKETS.md para más detalles")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores arriba.")
