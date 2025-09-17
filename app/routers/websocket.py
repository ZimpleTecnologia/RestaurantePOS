"""
Router para WebSockets
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional

from app.websocket_manager import websocket_endpoint, manager, WebSocketEvents
from app.models.user import User, UserRole
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/pedidos")
async def websocket_pedidos(
    websocket: WebSocket,
    user_type: str = Query(default="admin", description="Tipo de usuario: meseros, cocina, admin")
):
    """WebSocket para comunicación de pedidos en tiempo real"""
    await websocket_endpoint(websocket, user_type)


@router.websocket("/cocina")
async def websocket_cocina(websocket: WebSocket):
    """WebSocket específico para cocina"""
    await websocket_endpoint(websocket, "cocina")


@router.websocket("/meseros")
async def websocket_meseros(websocket: WebSocket):
    """WebSocket específico para meseros"""
    await websocket_endpoint(websocket, "meseros")


@router.websocket("/admin")
async def websocket_admin(websocket: WebSocket):
    """WebSocket específico para administradores"""
    await websocket_endpoint(websocket, "admin")


@router.get("/status")
async def get_websocket_status():
    """Obtener estado de las conexiones WebSocket"""
    return {
        "connections": manager.get_connection_count(),
        "total_connections": sum(manager.get_connection_count().values()),
        "available_endpoints": [
            "/ws/pedidos?user_type=meseros",
            "/ws/pedidos?user_type=cocina", 
            "/ws/pedidos?user_type=admin",
            "/ws/cocina",
            "/ws/meseros",
            "/ws/admin"
        ]
    }


@router.post("/test/broadcast")
async def test_broadcast(
    message: str,
    user_type: str = "all",
    current_user: User = Depends(get_current_user)
):
    """Endpoint de prueba para enviar mensajes broadcast (solo admin)"""
    if current_user.role != UserRole.ADMIN:
        return {"error": "Solo administradores pueden usar este endpoint"}
    
    test_data = {
        "message": message,
        "from": current_user.full_name,
        "user_type": user_type
    }
    
    if user_type == "all":
        await manager.broadcast_to_all(WebSocketEvents.create_event("test_message", test_data))
    else:
        await manager.broadcast_to_type(WebSocketEvents.create_event("test_message", test_data), user_type)
    
    return {
        "message": f"Mensaje enviado a {user_type}",
        "connections": manager.get_connection_count()
    }


