"""WebSocket package"""
from app.websockets.manager import ConnectionManager

websocket_manager = ConnectionManager()

__all__ = ["websocket_manager"]

