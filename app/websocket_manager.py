"""
Gestor de WebSockets para comunicación en tiempo real
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Gestor de conexiones WebSocket"""
    
    def __init__(self):
        # Diccionario para almacenar conexiones por tipo de usuario
        self.active_connections: Dict[str, List[WebSocket]] = {
            "meseros": [],
            "cocina": [],
            "admin": []
        }
    
    async def connect(self, websocket: WebSocket, user_type: str):
        """Conectar un WebSocket"""
        await websocket.accept()
        
        if user_type not in self.active_connections:
            user_type = "admin"  # Default para tipos no reconocidos
        
        self.active_connections[user_type].append(websocket)
        print(f"🔌 Usuario {user_type} conectado. Total conexiones: {len(self.active_connections[user_type])}")
    
    def disconnect(self, websocket: WebSocket, user_type: str):
        """Desconectar un WebSocket"""
        if user_type in self.active_connections:
            if websocket in self.active_connections[user_type]:
                self.active_connections[user_type].remove(websocket)
                print(f"🔌 Usuario {user_type} desconectado. Total conexiones: {len(self.active_connections[user_type])}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Enviar mensaje a una conexión específica"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"❌ Error enviando mensaje personal: {e}")
    
    async def broadcast_to_type(self, message: str, user_type: str):
        """Enviar mensaje a todos los usuarios de un tipo específico"""
        if user_type not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[user_type]:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"❌ Error enviando mensaje a {user_type}: {e}")
                disconnected.append(connection)
        
        # Remover conexiones que fallaron
        for connection in disconnected:
            self.active_connections[user_type].remove(connection)
    
    async def broadcast_to_all(self, message: str):
        """Enviar mensaje a todos los usuarios conectados"""
        for user_type in self.active_connections:
            await self.broadcast_to_type(message, user_type)
    
    def get_connection_count(self) -> Dict[str, int]:
        """Obtener número de conexiones por tipo"""
        return {
            user_type: len(connections) 
            for user_type, connections in self.active_connections.items()
        }


# Instancia global del gestor de conexiones
manager = ConnectionManager()


class WebSocketEvents:
    """Clase para manejar eventos de WebSocket"""
    
    @staticmethod
    def create_event(event_type: str, data: Dict[str, Any]) -> str:
        """Crear un evento JSON"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(event)
    
    @staticmethod
    async def notify_new_order(order_data: Dict[str, Any]):
        """Notificar nuevo pedido a cocina"""
        message = WebSocketEvents.create_event("nuevo_pedido", {
            "order_id": order_data.get("id"),
            "order_number": order_data.get("order_number"),
            "table_number": order_data.get("table_number"),
            "waiter_name": order_data.get("waiter_name"),
            "items_count": order_data.get("items_count"),
            "total_amount": str(order_data.get("total_amount")),
            "created_at": order_data.get("created_at")
        })
        
        await manager.broadcast_to_type(message, "cocina")
        await manager.broadcast_to_type(message, "admin")
        print("📢 Notificación de nuevo pedido enviada a cocina")
    
    @staticmethod
    async def notify_order_status_change(order_data: Dict[str, Any]):
        """Notificar cambio de estado de pedido"""
        message = WebSocketEvents.create_event("pedido_estado_cambiado", {
            "order_id": order_data.get("id"),
            "order_number": order_data.get("order_number"),
            "estado_anterior": order_data.get("estado_anterior"),
            "estado_nuevo": order_data.get("estado_nuevo"),
            "table_number": order_data.get("table_number"),
            "waiter_name": order_data.get("waiter_name"),
            "updated_at": order_data.get("updated_at")
        })
        
        # Notificar a todos los tipos de usuario
        await manager.broadcast_to_all(message)
        print("📢 Notificación de cambio de estado enviada a todos")
    
    @staticmethod
    async def notify_menu_updated(menu_data: Dict[str, Any]):
        """Notificar actualización de menú"""
        message = WebSocketEvents.create_event("menu_actualizado", {
            "menu_id": menu_data.get("id"),
            "fecha": menu_data.get("fecha"),
            "nombre": menu_data.get("nombre"),
            "precio": str(menu_data.get("precio"))
        })
        
        await manager.broadcast_to_type(message, "meseros")
        await manager.broadcast_to_type(message, "admin")
        print("📢 Notificación de menú actualizado enviada")
    
    @staticmethod
    async def notify_kitchen_alert(alert_data: Dict[str, Any]):
        """Notificar alerta de cocina"""
        message = WebSocketEvents.create_event("alerta_cocina", {
            "type": alert_data.get("type"),
            "message": alert_data.get("message"),
            "order_id": alert_data.get("order_id"),
            "priority": alert_data.get("priority", "normal")
        })
        
        await manager.broadcast_to_type(message, "cocina")
        await manager.broadcast_to_type(message, "admin")
        print("🚨 Alerta de cocina enviada")


async def websocket_endpoint(websocket: WebSocket, user_type: str = "admin"):
    """Endpoint principal de WebSocket"""
    await manager.connect(websocket, user_type)
    
    try:
        while True:
            # Mantener la conexión viva y escuchar mensajes
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                event_type = message.get("type")
                
                if event_type == "ping":
                    # Responder a ping con pong
                    pong_message = WebSocketEvents.create_event("pong", {
                        "message": "Conexión activa",
                        "user_type": user_type,
                        "connections": manager.get_connection_count()
                    })
                    await manager.send_personal_message(pong_message, websocket)
                
                elif event_type == "get_status":
                    # Enviar estado actual
                    status_message = WebSocketEvents.create_event("status", {
                        "connections": manager.get_connection_count(),
                        "user_type": user_type,
                        "server_time": datetime.now().isoformat()
                    })
                    await manager.send_personal_message(status_message, websocket)
                
                else:
                    print(f"📨 Mensaje recibido de {user_type}: {event_type}")
                    
            except json.JSONDecodeError:
                print(f"❌ Error decodificando JSON de {user_type}")
            except Exception as e:
                print(f"❌ Error procesando mensaje de {user_type}: {e}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_type)
        print(f"🔌 Usuario {user_type} desconectado")
    except Exception as e:
        print(f"❌ Error en WebSocket de {user_type}: {e}")
        manager.disconnect(websocket, user_type)


